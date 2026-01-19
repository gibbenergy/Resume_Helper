import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { PersonalInfoForm } from '@/components/resume/PersonalInfoForm';
import { EducationForm } from '@/components/resume/EducationForm';
import { ExperienceForm } from '@/components/resume/ExperienceForm';
import { SkillsForm } from '@/components/resume/SkillsForm';
import { ProjectsForm } from '@/components/resume/ProjectsForm';
import { CertificationsForm } from '@/components/resume/CertificationsForm';
import { OthersForm } from '@/components/resume/OthersForm';
import { AIResumeHelper } from '@/components/ai/AIResumeHelper';
import { ApplicationTracker } from '@/components/applications/ApplicationTracker';
import { PDFGenerator } from '@/components/pdf/PDFGenerator';

export function MainLayout() {
  const [activeTab, setActiveTab] = useState('personal');
  
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-8">
        <div className="flex items-center justify-center gap-3 mb-8">
          <h1 className="text-4xl font-bold">Resume Helper</h1>
          <Badge variant="outline" className="text-xs px-2 py-1">
            v1.0
          </Badge>
        </div>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="bg-background border-b mb-6">
            <TabsList className="grid w-full grid-cols-10 bg-transparent h-auto p-0">
              <TabsTrigger 
                value="personal"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Personal Info
              </TabsTrigger>
              <TabsTrigger 
                value="education"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Education
              </TabsTrigger>
              <TabsTrigger 
                value="experience"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Experience
              </TabsTrigger>
              <TabsTrigger 
                value="skills"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Skills
              </TabsTrigger>
              <TabsTrigger 
                value="projects"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Projects
              </TabsTrigger>
              <TabsTrigger 
                value="certifications"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Certifications
              </TabsTrigger>
              <TabsTrigger 
                value="others"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Others
              </TabsTrigger>
              <TabsTrigger 
                value="export"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Import/Export
              </TabsTrigger>
              <TabsTrigger 
                value="ai"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                AI Helper
              </TabsTrigger>
              <TabsTrigger 
                value="applications"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
              >
                Applications
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="personal">
            <PersonalInfoForm />
          </TabsContent>

          <TabsContent value="education">
            <EducationForm />
          </TabsContent>

          <TabsContent value="experience">
            <ExperienceForm />
          </TabsContent>

          <TabsContent value="skills">
            <SkillsForm />
          </TabsContent>

          <TabsContent value="projects">
            <ProjectsForm />
          </TabsContent>

          <TabsContent value="certifications">
            <CertificationsForm />
          </TabsContent>

          <TabsContent value="others">
            <OthersForm />
          </TabsContent>

          <TabsContent value="export">
            <PDFGenerator />
          </TabsContent>

          <TabsContent value="ai">
            <AIResumeHelper />
          </TabsContent>

          <TabsContent value="applications">
            <ApplicationTracker isActive={activeTab === 'applications'} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

