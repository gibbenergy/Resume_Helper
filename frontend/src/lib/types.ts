// Resume data types
export interface PersonalInfo {
  name_prefix?: string;
  email?: string;
  full_name?: string;
  phone?: string;
  current_address?: string;
  location?: string;
  citizenship?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  summary?: string;
  expected_salary?: string;
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study?: string;
  gpa?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}

export interface Experience {
  company: string;
  position: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  achievements?: string[];
}

export interface Skill {
  category: string;
  name: string;
  proficiency?: string;
}

export interface Project {
  name: string;
  description: string;
  technologies?: string;
  url?: string;
  start_date?: string;
  end_date?: string;
}

export interface Certification {
  name: string;
  issuer: string;
  date_obtained?: string;
  credential_id?: string;
  url?: string;
}

export interface ResumeData {
  personal_info: PersonalInfo;
  education: Education[];
  experience: Experience[];
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
  others?: Record<string, any>;
}

// AI result types
export interface JobAnalysisResult {
  success: boolean;
  analysis: string;
  match_score?: number;
  summary?: string;
  model?: string;
  usage?: any;
}

export interface TailoredResumeResult {
  success: boolean;
  content: string;
  model?: string;
  usage?: any;
}

export interface CoverLetterResult {
  success: boolean;
  content: string;
  model?: string;
  usage?: any;
}

export interface ImprovementSuggestionsResult {
  success: boolean;
  content: string;
  suggestions?: string[];
  model?: string;
  usage?: any;
}

// Provider info types
export interface ModelsInfo {
  success: boolean;
  models: string[];
  default?: string;
}

// Application tracker types
export interface Application {
  id: number;
  job_url: string;
  company: string;
  position: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  date_applied?: string;
  application_source?: string;
  priority?: string;
  status: string;
  description?: string;
  notes?: string;
  match_score?: number;
  hr_contact?: string;
  hiring_manager?: string;
  recruiter?: string;
  referral?: string;
  requirements?: string[];
  analysis_data?: Record<string, any>;
  interview_pipeline?: Record<string, any>;
  timeline?: Array<Record<string, any>>;
  next_actions?: string[];
  tags?: string[];
}

export interface Interview {
  id?: number;
  date: string;
  type: string;
  notes?: string;
  interviewer?: string;
}

export interface Document {
  id?: number;
  type: string;
  filename: string;
  uploaded_at?: string;
}
