import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertTriangle } from 'lucide-react';

interface SavedProfile {
  id: string;
  name: string;
}

interface SaveProfileDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultName: string;
  existingProfiles: SavedProfile[];
  onSave: (profileName: string) => void;
}

export function SaveProfileDialog({
  open,
  onOpenChange,
  defaultName,
  existingProfiles,
  onSave,
}: SaveProfileDialogProps) {
  const [profileName, setProfileName] = useState(defaultName);

  // Update profile name when dialog opens with new default
  useEffect(() => {
    if (open) {
      setProfileName(defaultName);
    }
  }, [open, defaultName]);

  const existingProfile = existingProfiles.find(
    (p) => p.name.toLowerCase() === profileName.toLowerCase()
  );

  const handleSave = () => {
    if (profileName.trim()) {
      onSave(profileName.trim());
      onOpenChange(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && profileName.trim()) {
      handleSave();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Save Profile</DialogTitle>
          <DialogDescription>
            Enter a name for this resume profile. You can create multiple versions for different job applications.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="profile-name">Profile Name</Label>
            <Input
              id="profile-name"
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g., Sarah Chen - Process Engineer"
              autoFocus
            />
          </div>

          {existingProfile && (
            <div className="flex items-start gap-2 rounded-md bg-yellow-500/10 p-3 text-sm text-yellow-600 dark:text-yellow-500">
              <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>
                A profile with this name already exists and will be updated.
              </span>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!profileName.trim()}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
