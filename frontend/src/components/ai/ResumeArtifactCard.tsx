import { UserCircle, RefreshCw, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import type { ResumeData } from '@/lib/types';

interface ResumeArtifactCardProps {
  resumeData: ResumeData;
  isSynced: boolean;
  resumeJson: string;
  onUpdate: () => void;
}

export function ResumeArtifactCard({
  resumeData,
  isSynced,
  resumeJson,
  onUpdate,
}: ResumeArtifactCardProps) {
  const fullName = resumeData?.personal_info?.full_name || 'Not Set';
  const summary = resumeData?.personal_info?.summary || '';
  const summaryPreview = summary.length > 60 ? summary.substring(0, 60) + '...' : summary || 'No summary available';

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <UserCircle className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Active Resume</CardTitle>
        </div>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={onUpdate}
                className="h-8 w-8 group"
              >
                <RefreshCw className="h-4 w-4 group-hover:rotate-180 transition-transform duration-500" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Update Resume</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary View */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">{fullName}</p>
            {isSynced && (
              <Badge variant="outline" className="text-xs bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/50">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Synced
              </Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground line-clamp-2">{summaryPreview}</p>
        </div>

        {/* View JSON Source - Collapsible */}
        <Accordion type="single" collapsible>
          <AccordionItem value="json-source" className="border-none">
            <AccordionTrigger className="text-xs text-muted-foreground py-2">
              View JSON Source
            </AccordionTrigger>
            <AccordionContent>
              <Textarea
                rows={8}
                value={resumeJson || 'Click refresh to load your current resume data from all tabs.'}
                onChange={() => {}} // Read-only
                className="font-mono text-sm"
                readOnly
              />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}
