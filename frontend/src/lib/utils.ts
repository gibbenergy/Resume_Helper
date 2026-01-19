import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Format job analysis as markdown
export function formatAnalysisAsMarkdown(analysis: string): string {
  if (!analysis) return '';
  
  // If it's already formatted markdown, return it
  if (analysis.includes('##') || analysis.includes('**')) {
    return analysis;
  }
  
  // Otherwise, do basic formatting
  return analysis
    .split('\n\n')
    .map(paragraph => paragraph.trim())
    .filter(p => p.length > 0)
    .join('\n\n');
}

// Format improvement suggestions content
export function formatSuggestionsContent(content: string): string {
  if (!content) return '';
  
  // If it's already formatted, return it
  if (content.includes('##') || content.includes('- ') || content.includes('* ')) {
    return content;
  }
  
  // Otherwise, split by newlines and format as list
  const lines = content.split('\n').filter(line => line.trim());
  if (lines.length <= 1) return content;
  
  return lines.map(line => `- ${line.trim()}`).join('\n');
}

// Extract match score from analysis text
export function extractMatchScore(analysis: string): number | null {
  if (!analysis) return null;
  
  // Look for patterns like "Match Score: 85%" or "Score: 85/100"
  const patterns = [
    /match\s+score[:\s]+(\d+)%/i,
    /score[:\s]+(\d+)\/100/i,
    /(\d+)%\s+match/i,
    /(\d+)\s*\/\s*100/,
  ];
  
  for (const pattern of patterns) {
    const match = analysis.match(pattern);
    if (match && match[1]) {
      const score = parseInt(match[1], 10);
      if (score >= 0 && score <= 100) {
        return score;
      }
    }
  }
  
  return null;
}

// Format date for display
export function formatDate(dateString?: string): string {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}

// Truncate text with ellipsis
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

// Convert string to title case
export function toTitleCase(text: string): string {
  if (!text) return '';
  return text
    .toLowerCase()
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Format location string
export function formatLocation(city?: string, state?: string, country?: string): string {
  const parts = [city, state, country].filter(Boolean);
  return parts.join(', ');
}

// Parse markdown analysis into structured data
export function parseMarkdownToAnalysis(markdown: string): { sections: Array<{ title: string; content: string }> } {
  if (!markdown) return { sections: [] };
  
  const sections: Array<{ title: string; content: string }> = [];
  const lines = markdown.split('\n');
  let currentSection: { title: string; content: string } | null = null;
  
  for (const line of lines) {
    // Check if line is a heading (starts with ##)
    if (line.trim().startsWith('##')) {
      // Save previous section if exists
      if (currentSection) {
        sections.push(currentSection);
      }
      // Start new section
      currentSection = {
        title: line.replace(/^#+\s*/, '').trim(),
        content: ''
      };
    } else if (currentSection && line.trim()) {
      // Add content to current section
      currentSection.content += (currentSection.content ? '\n' : '') + line;
    }
  }
  
  // Add last section
  if (currentSection) {
    sections.push(currentSection);
  }
  
  return { sections };
}
