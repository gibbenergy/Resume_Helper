"""
PDF Generation Module using Playwright

This module provides a modern interface for generating PDFs from HTML content
using Playwright (Chromium).
"""

import asyncio
import logging
import os
import tempfile
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import warnings

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class PlaywrightPDFGenerator:
    """
    PDF generator using Playwright (Chromium) browser engine.
    
    Provides both async and sync interfaces for generating PDFs from HTML content.
    Designed to replace WeasyPrint with better CSS support and no system dependencies.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self._browser_lock = asyncio.Lock()
    
    async def _ensure_browser(self):
        """Ensure browser is launched and ready"""
        async with self._browser_lock:
            if self.browser is None or (self.browser is not None and not self.browser.is_connected()):
                try:
                    if self.browser is not None:
                        try:
                            await self.browser.close()
                        except:
                            pass
                        self.browser = None
                    
                    if self.playwright is not None:
                        try:
                            await self.playwright.stop()
                        except:
                            pass
                        self.playwright = None
                    
                    logger.info("Starting Playwright...")
                    self.playwright = await async_playwright().start()
                    logger.info("Playwright started, launching browser...")
                    
                    # Launch browser with optimized settings for PDF generation
                    self.browser = await self.playwright.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--no-first-run',
                            '--disable-gpu'
                        ]
                    )
                    logger.info("Browser launched successfully")
                    
                    if not self.browser.is_connected():
                        raise RuntimeError("Browser launched but is not connected")
                        
                except Exception as e:
                    self.browser = None
                    if self.playwright:
                        try:
                            await self.playwright.stop()
                        except:
                            pass
                        self.playwright = None
                    
                    logger.error(f"Failed to launch browser: {e}")
                    import traceback
                    logger.error(f"Browser launch traceback: {traceback.format_exc()}")
                    raise RuntimeError(f"Browser launch failed: {e}")
    
    async def _setup_page_for_pdf(self, page, page_size: str = 'A4', margin: Optional[Dict] = None):
        """Configure page settings optimized for PDF generation"""
        
        viewport_sizes = {
            'A4': {'width': 794, 'height': 1123},  # A4 in pixels at 96 DPI
            'Letter': {'width': 816, 'height': 1056},
            'Legal': {'width': 816, 'height': 1344}
        }
        
        viewport = viewport_sizes.get(page_size, viewport_sizes['A4'])
        await page.set_viewport_size(viewport)
        
        if margin is None:
            margin = {
                'top': '1cm',
                'bottom': '1cm', 
                'left': '1cm',
                'right': '1cm'
            }
        
        return margin
    
    async def _handle_base_url(self, html_content: str, base_url: Optional[str]) -> str:
        """
        Handle base URL functionality similar to WeasyPrint.
        Converts relative URLs to absolute URLs when base_url is provided.
        """
        if not base_url:
            return html_content
        
        if not base_url.endswith('/'):
            base_url += '/'
        
        if os.path.exists(base_url.rstrip('/')):
            base_url = f"file://{os.path.abspath(base_url.rstrip('/'))}"
            if not base_url.endswith('/'):
                base_url += '/'
        
        base_tag = f'<base href="{base_url}">'
        
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', f'<head>\n{base_tag}')
        else:
            html_content = f'{base_tag}\n{html_content}'
        
        return html_content
    
    async def generate_pdf_async(
        self,
        html_content: str,
        output_path: str,
        base_url: Optional[str] = None,
        page_size: str = 'A4',
        margin: Optional[Dict] = None,
        wait_for_fonts: bool = True,
        print_background: bool = True
    ) -> bool:
        """
        Generate PDF from HTML content asynchronously.
        
        Args:
            html_content: HTML content as string
            output_path: Path to save the PDF file
            base_url: Base URL for resolving relative paths (like WeasyPrint)
            page_size: Page size ('A4', 'Letter', 'Legal')
            margin: Dict with margin settings {'top': '1cm', 'bottom': '1cm', etc.}
            wait_for_fonts: Whether to wait for fonts to load
            print_background: Whether to include background graphics
            
        Returns:
            bool: True if successful, False otherwise
        """
        playwright = None
        browser = None
        page = None
        
        try:
            logger.info("Starting fresh Playwright instance for PDF generation...")
            playwright = await async_playwright().start()
            
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--disable-gpu'
                ]
            )
            logger.info("Fresh browser launched successfully")
            
            page = await browser.new_page()
            
            try:
                margin_settings = await self._setup_page_for_pdf(page, page_size, margin)
                processed_html = await self._handle_base_url(html_content, base_url)
                await page.set_content(processed_html, wait_until='networkidle')
                
                if wait_for_fonts:
                    try:
                        await page.evaluate('document.fonts.ready')
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Font loading wait failed (continuing anyway): {e}")
                
                pdf_options = {
                    'format': page_size,
                    'margin': margin_settings,
                    'print_background': print_background,
                    'prefer_css_page_size': True,  # Respect CSS page size
                    'display_header_footer': False
                }
                
                logger.info(f"Generating PDF with options: {pdf_options}")
                pdf_bytes = await page.pdf(**pdf_options)
                
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    file_size = os.path.getsize(output_path)
                    logger.info(f"PDF generated successfully: {output_path} ({file_size:,} bytes)")
                    return True
                else:
                    logger.error("PDF file was not created or is empty")
                    return False
                    
            finally:
                if page:
                    try:
                        await page.close()
                        logger.info("Page closed successfully")
                    except Exception as e:
                        logger.warning(f"Error closing page: {e}")
                    
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
            
        finally:
            if browser:
                try:
                    await browser.close()
                    logger.info("Fresh browser closed successfully")
                except Exception as e:
                    logger.warning(f"Error closing fresh browser: {e}")
            
            if playwright:
                try:
                    await playwright.stop()
                    logger.info("Fresh Playwright stopped successfully")
                except Exception as e:
                    logger.warning(f"Error stopping fresh Playwright: {e}")
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            try:
                if self.browser.is_connected():
                    await self.browser.close()
                    logger.info("Browser closed successfully")
                else:
                    logger.info("Browser already disconnected")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
        
        if self.playwright:
            try:
                await self.playwright.stop()
                logger.info("Playwright stopped successfully")
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
                
        self.browser = None
        self.playwright = None


# Global PDF generator instance
_pdf_generator = None


async def get_pdf_generator() -> PlaywrightPDFGenerator:
    """Get or create the global PDF generator instance"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PlaywrightPDFGenerator()
    return _pdf_generator


async def generate_pdf_from_html(
    html_content: str,
    output_path: str,
    base_url: Optional[str] = None,
    page_size: str = 'A4',
    margin: Optional[Dict] = None
) -> bool:
    """
    Generate PDF from HTML content (async interface).
    
    This function provides the main async interface for PDF generation,
    replacing WeasyPrint's HTML().write_pdf() functionality.
    
    Args:
        html_content: HTML content as string
        output_path: Path to save the PDF file
        base_url: Base URL for resolving relative paths
        page_size: Page size ('A4', 'Letter', 'Legal')
        margin: Dict with margin settings
        
    Returns:
        bool: True if successful, False otherwise
    """
    generator = await get_pdf_generator()
    return await generator.generate_pdf_async(
        html_content, output_path, base_url, page_size, margin
    )


def generate_pdf_sync(
    html_content: str,
    output_path: str,
    base_url: Optional[str] = None,
    page_size: str = 'A4',
    margin: Optional[Dict] = None
    ) -> bool:
    """
    Generate PDF from HTML content (synchronous interface).
    
    This function provides a synchronous wrapper around the async PDF generation,
    maintaining compatibility with existing synchronous code that used WeasyPrint.
    
    Args:
        html_content: HTML content as string
        output_path: Path to save the PDF file  
        base_url: Base URL for resolving relative paths (equivalent to WeasyPrint's base_url)
        page_size: Page size ('A4', 'Letter', 'Legal')
        margin: Dict with margin settings
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(_run_pdf_generation(
                            html_content, output_path, base_url, page_size, margin
                        ))
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    generate_pdf_from_html(html_content, output_path, base_url, page_size, margin)
                )
        except RuntimeError:
            return asyncio.run(
                generate_pdf_from_html(html_content, output_path, base_url, page_size, margin)
            )
    except Exception as e:
        logger.error(f"Synchronous PDF generation failed: {e}")
        return False


async def _run_pdf_generation(html_content, output_path, base_url, page_size, margin):
    """Helper function for running PDF generation in a new event loop"""
    return await generate_pdf_from_html(html_content, output_path, base_url, page_size, margin)


async def cleanup_pdf_generator():
    """Clean up the global PDF generator instance"""
    global _pdf_generator
    if _pdf_generator:
        await _pdf_generator.cleanup()
        _pdf_generator = None


  
