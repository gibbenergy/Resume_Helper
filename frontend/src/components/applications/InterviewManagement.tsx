import { useState, useEffect } from 'react';
import { useApplicationStore } from '@/stores/applicationStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { X, Save, XCircle, CheckCircle2 } from 'lucide-react';
import type { InterviewRound } from '@/lib/types';
import { formatDate } from '@/lib/utils';

interface InterviewManagementProps {
  appId: string;
  onClose: () => void;
  dateApplied?: string;
}

export function InterviewManagement({ appId, onClose, dateApplied }: InterviewManagementProps) {
  const {
    selectedApplication,
    settings,
    selectedRound,
    fetchApplication,
    fetchSettings,
    updateInterviewRound,
    setSelectedRound,
  } = useApplicationStore();

  const [roundFormVisible, setRoundFormVisible] = useState(false);
  const [roundFormData, setRoundFormData] = useState<Partial<InterviewRound>>({
    status: 'not_started',
    date: new Date().toISOString().split('T')[0],
    time: '',
    location: '',
    interviewer: '',
    outcome: 'pending',
    notes: '',
  });

  useEffect(() => {
    if (!settings) {
      fetchSettings();
    }
    if (!selectedApplication || selectedApplication.id !== appId) {
      fetchApplication(appId);
    }
  }, [appId, settings, selectedApplication, fetchSettings, fetchApplication]);

  const defaultRounds = settings?.default_interview_rounds || [
    'phone_screen',
    'technical',
    'panel',
    'manager',
    'culture_fit',
    'final_round',
  ];

  const roundStatuses = settings?.interview_round_statuses || [
    'not_started',
    'scheduled',
    'completed',
    'cancelled',
    'rescheduled',
  ];

  const roundOutcomes = settings?.interview_round_outcomes || [
    'pending',
    'passed',
    'failed',
    'needs_follow_up',
  ];

  const interviewPipeline = selectedApplication?.interview_pipeline || {};

  const getCurrentRound = () => {
    for (let i = 0; i < defaultRounds.length; i++) {
      const roundName = defaultRounds[i];
      const roundData = interviewPipeline[roundName] || { status: 'not_started' };
      const status = roundData.status || 'not_started';

      // Active node is the first with status "scheduled" or "in_progress"
      if (status === 'scheduled' || status === 'in_progress') {
        return { roundName, index: i };
      } else if (status === 'completed') {
        const outcome = roundData.outcome || '';
        // If completed but not passed, this is the current (failed) node
        if (outcome !== 'passed') {
          return { roundName, index: i };
        }
        // If passed, continue to next round
      } else if (status === 'not_started') {
        // First not_started round is the current one
        return { roundName, index: i };
      } else if (status === 'cancelled' || status === 'on_hold') {
        return { roundName, index: i };
      }
    }
    return null;
  };

  const currentRoundInfo = getCurrentRound();

  const handleRoundClick = (roundName: string) => {
    const roundData = interviewPipeline[roundName] || {
      status: 'not_started',
      date: new Date().toISOString().split('T')[0],
      time: '',
      location: '',
      interviewer: '',
      outcome: 'pending',
      notes: '',
    };

    setRoundFormData({
      status: (roundData.status as any) || 'not_started',
      date: roundData.date || new Date().toISOString().split('T')[0],
      time: roundData.time || '',
      location: roundData.location || '',
      interviewer: roundData.interviewer || '',
      outcome: (roundData.outcome as any) || 'pending',
      notes: roundData.notes || '',
    });

    setSelectedRound(roundName);
    setRoundFormVisible(true);
  };

  const handleSaveRound = async () => {
    if (!selectedRound) return;

    const success = await updateInterviewRound(appId, selectedRound, roundFormData);
    if (success) {
      // Auto-advance: If status is completed and outcome is passed, automatically schedule next round
      if (roundFormData.status === 'completed' && roundFormData.outcome === 'passed') {
        const currentIndex = defaultRounds.findIndex(r => r === selectedRound);
        if (currentIndex >= 0 && currentIndex + 1 < defaultRounds.length) {
          const nextRoundName = defaultRounds[currentIndex + 1];
          const nextRoundData = interviewPipeline[nextRoundName] || {};
          
          // Only auto-advance if next round is not_started
          if (!nextRoundData.status || nextRoundData.status === 'not_started') {
            await updateInterviewRound(appId, nextRoundName, {
              ...nextRoundData,
              status: 'scheduled',
              date: nextRoundData.date || new Date().toISOString().split('T')[0],
              outcome: 'pending',
            });
          }
        }
      }
      
      setRoundFormVisible(false);
      setSelectedRound(null);
    }
  };

  const handleCancelRound = () => {
    setRoundFormVisible(false);
    setSelectedRound(null);
  };


  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'scheduled':
        return '📅';
      default:
        return '⭕';
    }
  };

  const getStatusText = (roundData: Partial<InterviewRound>) => {
    const status = roundData.status || 'not_started';
    if (status === 'completed') {
      const outcome = roundData.outcome || '';
      if (outcome && outcome !== 'pending') {
        return `Completed - ${outcome.charAt(0).toUpperCase() + outcome.slice(1)}`;
      }
      return 'Completed';
    } else if (status === 'scheduled') {
      return 'Scheduled';
    }
    return 'Not Started';
  };

  const getRoundDetails = (roundData: Partial<InterviewRound>) => {
    const parts: string[] = [];
    if (roundData.location) {
      parts.push(`📍 ${roundData.location}`);
    }
    if (roundData.interviewer) {
      parts.push(`👤 ${roundData.interviewer}`);
    }
    // Filter out auto-generated notes
    if (roundData.notes) {
      const autoGeneratedPatterns = [
        'went back to this round',
        'advanced from previous round',
        'round completed, advanced to next'
      ];
      const notesLower = roundData.notes.toLowerCase();
      const isAutoGenerated = autoGeneratedPatterns.some(pattern => 
        notesLower.includes(pattern)
      );
      
      if (!isAutoGenerated) {
        const notePreview =
          roundData.notes.length > 50
            ? roundData.notes.substring(0, 50) + '...'
            : roundData.notes;
        parts.push(notePreview);
      }
    }
    return parts.length > 0 ? parts.join(' | ') : '—';
  };

  // Create timeline nodes: Applied (first) + interview rounds
  const timelineNodes = [
    { name: 'Applied', key: 'applied', isFirst: true },
    ...defaultRounds.map(roundName => ({ name: roundName, key: roundName, isFirst: false }))
  ];

  const getNodeState = (node: typeof timelineNodes[0], nodeIndex: number) => {
    if (node.key === 'applied') {
      // Applied is always complete if we're viewing interviews
      return 'complete';
    }
    const roundData = interviewPipeline[node.key] || { status: 'not_started' };
    const status = roundData.status || 'not_started';
    const outcome = roundData.outcome || '';
    
    // Check if outcome is failed first (only if this specific node failed)
    if (status === 'completed' && outcome === 'failed') {
      return 'failed';
    }
    
    // Check if this node or any later node is completed (passed)
    if (isNodeCompleted(node, nodeIndex)) {
      return 'complete';
    } else if (status === 'scheduled' || status === 'in_progress' || currentRoundInfo?.roundName === node.key) {
      return 'active';
    }
    return 'incomplete';
  };

  // Check if a node is completed (passed) - either directly or implicitly via a later node
  // Note: If any later node is failed, we don't mark previous nodes as completed
  const isNodeCompleted = (node: typeof timelineNodes[0], nodeIndex: number) => {
    if (node.key === 'applied') return true;
    
    // Check if this node itself is completed
    const roundData = interviewPipeline[node.key] || {};
    if (roundData.status === 'completed' && roundData.outcome === 'passed') {
      return true;
    }
    
    // Check if any later node is completed (passed) - if so, this node is implicitly completed
    // But stop if we encounter a failed node (failed nodes stop progression)
    for (let i = nodeIndex + 1; i < timelineNodes.length; i++) {
      const laterNode = timelineNodes[i];
      if (laterNode.key === 'applied') continue;
      const laterRoundData = interviewPipeline[laterNode.key] || {};
      
      // If a later node is failed, stop - don't mark previous nodes as completed
      if (laterRoundData.status === 'completed' && laterRoundData.outcome === 'failed') {
        return false;
      }
      
      // If a later node is passed, this node is implicitly completed
      if (laterRoundData.status === 'completed' && laterRoundData.outcome === 'passed') {
        return true;
      }
    }
    
    return false;
  };

  const getNodeDate = (node: typeof timelineNodes[0]) => {
    if (node.key === 'applied') {
      return dateApplied ? formatDate(dateApplied) : '—';
    }
    const roundData = interviewPipeline[node.key] || {};
    const dateStr = roundData.date || '';
    const timeStr = roundData.time || '';
    return dateStr ? (timeStr ? `${dateStr} ${timeStr}` : dateStr) : '—';
  };

  return (
    <div className="flex-1 overflow-hidden p-6 flex flex-col">
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Timeline - Left Side */}
        <div className="flex-1 overflow-y-auto">
          <div className="relative">
            {/* Timeline line - positioned to align with center of nodes */}
            <div className="absolute left-8 top-8 bottom-8 w-0.5">
              {/* Base gray line */}
              <div className="absolute inset-0 bg-muted" />
              {/* Green segments for completed connections */}
              {timelineNodes.map((node, index) => {
                if (index === 0) return null; // Skip first node
                const prevNode = timelineNodes[index - 1];
                const isPrevCompleted = isNodeCompleted(prevNode, index - 1);
                
                // Show green line segment if previous node is completed
                if (isPrevCompleted) {
                  // Calculate position: from previous node center to current node center
                  // Each node takes ~80px (64px node + 16px spacing), center is at 32px from top of node
                  const nodeSpacing = 80;
                  const nodeCenterOffset = 32;
                  const segmentTop = (index - 1) * nodeSpacing + nodeCenterOffset;
                  const segmentBottom = index * nodeSpacing + nodeCenterOffset;
                  const segmentHeight = segmentBottom - segmentTop;
                  
                  return (
                    <div
                      key={`line-segment-${index}`}
                      className="absolute left-0 w-0.5 bg-green-500 z-0"
                      style={{
                        top: `${segmentTop}px`,
                        height: `${segmentHeight}px`,
                      }}
                    />
                  );
                }
                return null;
              })}
            </div>

            {/* Timeline nodes */}
            <div className="space-y-8">
              {timelineNodes.map((node, index) => {
                const state = getNodeState(node, index);
                const nodeDate = getNodeDate(node);
                const isCurrent = node.key !== 'applied' && currentRoundInfo?.roundName === node.key;
                const roundData = node.key !== 'applied' ? (interviewPipeline[node.key] || {}) : null;
                const isSelected = selectedRound === node.key;
                
                const displayName = node.key === 'applied' 
                  ? 'Applied' 
                  : node.name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());

                const details = roundData ? getRoundDetails(roundData as Partial<InterviewRound>) : null;

                return (
                  <div 
                    key={node.key} 
                    className={`relative flex items-center gap-4 cursor-pointer hover:opacity-80 transition-opacity ${isSelected ? 'bg-muted/50 rounded-lg p-2 -ml-2' : ''}`}
                    onClick={() => node.key !== 'applied' && handleRoundClick(node.key)}
                  >
                    {/* Node circle */}
                    <div className="relative z-10 flex-shrink-0">
                      {state === 'complete' ? (
                        <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center border-4 border-background shadow-lg">
                          <CheckCircle2 className="h-8 w-8 text-white" />
                        </div>
                      ) : state === 'failed' ? (
                        <div className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center border-4 border-background shadow-lg">
                          <XCircle className="h-8 w-8 text-white" />
                        </div>
                      ) : state === 'active' ? (
                        <div className="w-16 h-16 rounded-full border-4 border-green-500 flex items-center justify-center bg-background shadow-lg">
                          <div className="w-8 h-8 rounded-full bg-green-500 animate-pulse" />
                        </div>
                      ) : (
                        <div className="w-16 h-16 rounded-full bg-muted border-4 border-background flex items-center justify-center">
                          <div className="w-8 h-8 rounded-full bg-muted-foreground/30" />
                        </div>
                      )}
                    </div>

                    {/* Node content - same row */}
                    <div className="flex-1 flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <h3 className="text-base font-semibold">{displayName}</h3>
                        {isCurrent && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">
                            Current
                          </span>
                        )}
                      </div>
                      {nodeDate !== '—' && (
                        <span className="text-sm text-muted-foreground">• {nodeDate}</span>
                      )}
                      {details && details !== '—' && (
                        <span className="text-xs text-muted-foreground">• {details}</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Detail Panel - Right Side */}
        {roundFormVisible && selectedRound && (
          <div className="w-96 border-l pl-6 overflow-y-auto flex-shrink-0">
            <Card>
              <CardHeader>
                <CardTitle>
                  Edit {selectedRound.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="round-date">Date</Label>
                  <Input
                    id="round-date"
                    type="date"
                    value={roundFormData.date || ''}
                    onChange={(e) => setRoundFormData({ ...roundFormData, date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="round-time">Time</Label>
                  <Input
                    id="round-time"
                    type="time"
                    value={roundFormData.time || ''}
                    onChange={(e) => setRoundFormData({ ...roundFormData, time: e.target.value })}
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="round-location">Location</Label>
                  <Input
                    id="round-location"
                    value={roundFormData.location || ''}
                    onChange={(e) =>
                      setRoundFormData({ ...roundFormData, location: e.target.value })
                    }
                    placeholder="Office/Zoom"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="round-interviewer">Interviewer</Label>
                  <Input
                    id="round-interviewer"
                    value={roundFormData.interviewer || ''}
                    onChange={(e) =>
                      setRoundFormData({ ...roundFormData, interviewer: e.target.value })
                    }
                    placeholder="Name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="round-status">Status</Label>
                  <Select
                    value={roundFormData.status || 'not_started'}
                    onValueChange={(value) =>
                      setRoundFormData({
                        ...roundFormData,
                        status: value as InterviewRound['status'],
                      })
                    }
                  >
                    <SelectTrigger id="round-status">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {roundStatuses.map((status) => (
                        <SelectItem key={status} value={status}>
                          {status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="round-outcome">Outcome</Label>
                  <Select
                    value={roundFormData.outcome || 'pending'}
                    onValueChange={(value) =>
                      setRoundFormData({
                        ...roundFormData,
                        outcome: value as InterviewRound['outcome'],
                      })
                    }
                  >
                    <SelectTrigger id="round-outcome">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {roundOutcomes.map((outcome) => (
                        <SelectItem key={outcome} value={outcome}>
                          {outcome.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="round-notes">Notes</Label>
                  <Textarea
                    id="round-notes"
                    rows={3}
                    value={roundFormData.notes || ''}
                    onChange={(e) =>
                      setRoundFormData({ ...roundFormData, notes: e.target.value })
                    }
                    placeholder="Feedback, preparation notes, next steps..."
                  />
                </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleSaveRound}>
                    <Save className="mr-2 h-4 w-4" />
                    Save
                  </Button>
                  <Button variant="secondary" onClick={handleCancelRound}>
                    <XCircle className="mr-2 h-4 w-4" />
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

