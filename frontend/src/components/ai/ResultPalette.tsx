import { FileText, Target, Mail, Lightbulb, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import type { JobAnalysisResult, TailoredResumeResult, CoverLetterResult, ImprovementSuggestionsResult } from '@/lib/types';

interface ResultPaletteProps {
  onResultClick: (type: 'summary' | 'tailored' | 'cover-letter' | 'suggestions') => void;
  jobAnalysis?: JobAnalysisResult;
  tailoredResume?: TailoredResumeResult;
  coverLetter?: CoverLetterResult;
  improvementSuggestions?: ImprovementSuggestionsResult;
}

interface ResultBadge {
  type: 'summary' | 'tailored' | 'cover-letter' | 'suggestions';
  label: string;
  icon: React.ReactNode;
  available: boolean;
}

export function ResultPalette({
  onResultClick,
  jobAnalysis,
  tailoredResume,
  coverLetter,
  improvementSuggestions,
}: ResultPaletteProps) {
  const results: ResultBadge[] = [
    {
      type: 'summary',
      label: 'Job Analysis',
      icon: <FileText className="h-4 w-4" />,
      available: !!jobAnalysis?.analysis,
    },
    {
      type: 'tailored',
      label: 'Tailored Resume',
      icon: <Target className="h-4 w-4" />,
      available: !!tailoredResume?.tailored_resume,
    },
    {
      type: 'cover-letter',
      label: 'Cover Letter',
      icon: <Mail className="h-4 w-4" />,
      available: !!coverLetter?.body_content,
    },
    {
      type: 'suggestions',
      label: 'Skill Gap Analysis',
      icon: <Lightbulb className="h-4 w-4" />,
      available: !!improvementSuggestions?.content,
    },
  ];

  const availableResults = results.filter((r) => r.available);

  if (availableResults.length === 0) {
    return (
      <div className="flex items-center justify-center h-[200px] border-2 border-dashed border-muted rounded-lg">
        <div className="text-center space-y-2">
          <FileText className="h-12 w-12 mx-auto text-muted-foreground opacity-50" />
          <p className="text-muted-foreground">Results will appear here after AI operations complete</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <Label className="text-base font-semibold">Generated Artifacts</Label>
      <div className="flex flex-wrap gap-3">
        {results.map((result) => {
          if (!result.available) return null;
          
          return (
            <Badge
              key={result.type}
              variant="secondary"
              className="cursor-pointer hover:bg-primary hover:text-primary-foreground hover:scale-105 transition-all duration-200 px-4 py-2 h-auto gap-2 group border shadow-sm"
              onClick={() => onResultClick(result.type)}
            >
              <span className="text-primary group-hover:text-primary-foreground transition-colors flex-shrink-0">
                {result.icon}
              </span>
              <span className="text-sm font-medium whitespace-nowrap">{result.label}</span>
              <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
            </Badge>
          );
        })}
      </div>
    </div>
  );
}
 
