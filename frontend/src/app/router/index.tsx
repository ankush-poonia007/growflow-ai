import { createBrowserRouter } from 'react-router';
import { RootLayout } from '@/app/layouts/RootLayout';
import { PublicLayout } from '@/app/layouts/PublicLayout';
import { AuthenticatedLayout } from '@/app/layouts/AuthenticatedLayout';
import { Contact } from '@/pages/Contact/Contact';
import { Documentation } from '@/pages/Documentation/Documentation';
import { Features } from '@/pages/Features/Features';
import { Landing } from '@/pages/Landing/Landing';
import { Showcase } from '@/pages/Showcase/Showcase';

import { StudentSignIn } from '@/pages/Auth/StudentSignIn/StudentSignIn';
import { StudentRegister } from '@/pages/Auth/StudentRegister/StudentRegister';
import { StudentPasswordRecovery } from '@/pages/Auth/StudentPasswordRecovery/StudentPasswordRecovery';
import { StudentDashboard } from '@/pages/Student/StudentDashboard';
import { StudentProjects } from '@/pages/Student/StudentProjects';
import { StudentProjectCreate } from '@/pages/Student/StudentProjectCreate';
import { StudentMentorProjectCatalog } from '@/pages/Student/StudentMentorProjectCatalog';
import { StudentMentorProjectDetail } from '@/pages/Student/StudentMentorProjectDetail';
import { StudentProjectProfile } from '@/pages/Student/StudentProjectProfile';
import { StudentAssessment } from '@/pages/Student/StudentAssessment';
import { StudentBlueprint } from '@/pages/Student/StudentBlueprint';
import { StudentProjectOverview } from '@/pages/Student/StudentProjectOverview/StudentProjectOverview';
import { StudentBlueprintWorkspace } from '@/pages/Student/StudentBlueprintWorkspace/StudentBlueprintWorkspace';
import { StudentBlueprintDocumentViewer } from '@/pages/Student/StudentBlueprintDocumentViewer/StudentBlueprintDocumentViewer';
import { StudentTasks } from '@/pages/Student/StudentTasks/StudentTasks';
import { StudentTaskDetail } from '@/pages/Student/StudentTaskDetail/StudentTaskDetail';
import { StudentMilestones } from '@/pages/Student/StudentMilestones/StudentMilestones';
import { StudentMilestoneDetail } from '@/pages/Student/StudentMilestoneDetail/StudentMilestoneDetail';
import { StudentRisks } from '@/pages/Student/StudentRisks/StudentRisks';
import { StudentRiskDetail } from '@/pages/Student/StudentRiskDetail/StudentRiskDetail';
import { StudentRoadmap } from '@/pages/Student/StudentRoadmap/StudentRoadmap';
import { StudentDocuments } from '@/pages/Student/StudentDocuments/StudentDocuments';
import { StudentDocumentDetail } from '@/pages/Student/StudentDocumentDetail/StudentDocumentDetail';
import { StudentGitHub } from '@/pages/Student/StudentGitHub/StudentGitHub';
import { StudentActivity } from '@/pages/Student/StudentActivity/StudentActivity';
import { StudentAIMentor } from '@/pages/Student/StudentAIMentor/StudentAIMentor';
import { StudentHelpRequests } from '@/pages/Student/StudentHelpRequests/StudentHelpRequests';
import { StudentMentorFeedback } from '@/pages/Student/StudentMentorFeedback/StudentMentorFeedback';
import { StudentProjectChanges } from '@/pages/Student/StudentProjectChanges/StudentProjectChanges';
import { StudentProjectChangeDetail } from '@/pages/Student/StudentProjectChangeDetail/StudentProjectChangeDetail';
import { StudentGroups } from '@/pages/Student/StudentGroups/StudentGroups';

import { MentorSignIn } from '@/pages/Auth/MentorSignIn/MentorSignIn';
import { MentorRegister } from '@/pages/Auth/MentorRegister/MentorRegister';
import { MentorPasswordRecovery } from '@/pages/Auth/MentorPasswordRecovery/MentorPasswordRecovery';
import { MentorLayout } from '@/app/layouts/MentorLayout';
import { MentorOverview } from '@/pages/Mentor/MentorOverview/MentorOverview';
import { GroupsDirectory } from '@/pages/Mentor/GroupsDirectory/GroupsDirectory';
import { GroupCreate } from '@/pages/Mentor/GroupCreate/GroupCreate';
import { GroupWorkspace } from '@/pages/Mentor/GroupWorkspace/GroupWorkspace';
import { GroupStudents } from '@/pages/Mentor/GroupStudents/GroupStudents';
import { GroupProjects } from '@/pages/Mentor/GroupProjects/GroupProjects';
import { GroupAtRisk } from '@/pages/Mentor/GroupAtRisk/GroupAtRisk';
import { ProjectsDirectory } from '@/pages/Mentor/ProjectsDirectory/ProjectsDirectory';
import { DefinitionDetail } from '@/pages/Mentor/DefinitionDetail/DefinitionDetail';
import { DefinitionCreate } from '@/pages/Mentor/DefinitionCreate/DefinitionCreate';
import { DefinitionEdit } from '@/pages/Mentor/DefinitionEdit/DefinitionEdit';
import { DefinitionAssign } from '@/pages/Mentor/DefinitionAssign/DefinitionAssign';
import { StudentsDirectory } from '@/pages/Mentor/StudentsDirectory/StudentsDirectory';
import { StudentDetail } from '@/pages/Mentor/StudentDetail/StudentDetail';
import { StudentProjects as MentorStudentProjects } from '@/pages/Mentor/StudentProjects/StudentProjects';
import { MentorProjectsDirectory } from '@/pages/Mentor/InstancesDirectory/MentorProjectsDirectory';
import { ProjectInstances } from '@/pages/Mentor/ProjectInstances/ProjectInstances';
import { ProjectInstanceDetail } from '@/pages/Mentor/ProjectInstanceDetail/ProjectInstanceDetail';
import { MentorInstanceBlueprint } from '@/pages/Mentor/InstanceBlueprint/MentorInstanceBlueprint';
import { MentorInstanceTasks } from '@/pages/Mentor/InstanceTasks/MentorInstanceTasks';
import { MentorInstanceMilestones } from '@/pages/Mentor/InstanceMilestones/MentorInstanceMilestones';
import { MentorInstanceRisks } from '@/pages/Mentor/InstanceRisks/MentorInstanceRisks';
import { MentorInstanceDocuments } from '@/pages/Mentor/InstanceDocuments/MentorInstanceDocuments';
import { MentorInstanceGitHub } from '@/pages/Mentor/InstanceGitHub/MentorInstanceGitHub';
import { MentorInstanceActivity } from '@/pages/Mentor/InstanceActivity/MentorInstanceActivity';
import { MentorInstanceNotes } from '@/pages/Mentor/InstanceNotes/MentorInstanceNotes';
import { MentorHelpRequests } from '@/pages/Mentor/HelpRequests/MentorHelpRequests';
import { AtRiskDirectory } from '@/pages/Mentor/AtRiskDirectory/AtRiskDirectory';
import { AtRiskDetail } from '@/pages/Mentor/AtRiskDetail/AtRiskDetail';
import { GroupActivity } from '@/pages/Mentor/GroupActivity/GroupActivity';
import { GroupAIMentor } from '@/pages/Mentor/GroupAIMentor/GroupAIMentor';
import { MentorStudentActivity } from '@/pages/Mentor/MentorStudentActivity/MentorStudentActivity';
import { MentorActivity } from '@/pages/Mentor/MentorActivity/MentorActivity';
import { MentorAI } from '@/pages/Mentor/MentorAI/MentorAI';
import { MentorProfile } from '@/pages/Mentor/MentorProfile/MentorProfile';
import { MentorSettings } from '@/pages/Mentor/MentorSettings/MentorSettings';
import { StudentProfilePage } from '@/pages/Student/StudentProfile/StudentProfile';
import { StudentSettingsPage } from '@/pages/Student/StudentSettings/StudentSettings';
import { AdminLayout } from '@/app/layouts/AdminLayout';
import { AdminOverview } from '@/pages/Admin/AdminOverview/AdminOverview';
import { MentorDirectory } from '@/pages/Admin/MentorDirectory/MentorDirectory';
import { MentorDetail as AdminMentorDetail } from '@/pages/Admin/MentorDetail/MentorDetail';
import { StudentDirectory as AdminStudentDirectory } from '@/pages/Admin/StudentDirectory/StudentDirectory';
import { StudentDetail as AdminStudentDetail } from '@/pages/Admin/StudentDetail/StudentDetail';
import { AdminProfile } from '@/pages/Admin/AdminProfile/AdminProfile';
import { AdminSettings } from '@/pages/Admin/AdminSettings/AdminSettings';
import { GroupsDirectory as AdminGroupsDirectory } from '@/pages/Admin/GroupsDirectory/GroupsDirectory';
import { GroupDetail as AdminGroupDetail } from '@/pages/Admin/GroupDetail/GroupDetail';
import { ProjectsDirectory as AdminProjectsDirectory } from '@/pages/Admin/ProjectsDirectory/ProjectsDirectory';
import { DefinitionsMonitoring as AdminDefinitionsMonitoring } from '@/pages/Admin/DefinitionsMonitoring/DefinitionsMonitoring';
import { InstancesMonitoring as AdminInstancesMonitoring } from '@/pages/Admin/InstancesMonitoring/InstancesMonitoring';
import { InstanceDetail as AdminInstanceDetail } from '@/pages/Admin/InstanceDetail/InstanceDetail';
import { SystemHealth as AdminSystemHealth } from '@/pages/Admin/SystemHealth/SystemHealth';
import { ComponentDetail as AdminComponentDetail } from '@/pages/Admin/ComponentDetail/ComponentDetail';
import { SecurityOverview as AdminSecurityOverview } from '@/pages/Admin/SecurityOverview/SecurityOverview';
import { AuditLog as AdminAuditLog } from '@/pages/Admin/AuditLog/AuditLog';
import { InvestigationRequests as AdminInvestigationRequests } from '@/pages/Admin/InvestigationRequests/InvestigationRequests';
import { InvestigationDetail as AdminInvestigationDetail } from '@/pages/Admin/InvestigationDetail/InvestigationDetail';
import { DocumentsRAG as AdminDocumentsRAG } from '@/pages/Admin/DocumentsRAG/DocumentsRAG';
import { RAGMonitoring as AdminRAGMonitoring } from '@/pages/Admin/RAGMonitoring/RAGMonitoring';
import { DocumentGeneration as AdminDocumentGeneration } from '@/pages/Admin/DocumentGeneration/DocumentGeneration';
import { PlatformAnalytics as AdminPlatformAnalytics } from '@/pages/Admin/PlatformAnalytics/PlatformAnalytics';
import { AnalyticsDetail as AdminAnalyticsDetail } from '@/pages/Admin/AnalyticsDetail/AnalyticsDetail';
import { AIObservatory as AdminAIObservatory } from '@/pages/Admin/AIObservatory/AIObservatory';
import { AIUsage as AdminAIUsage } from '@/pages/Admin/AIUsage/AIUsage';
import { AIExecutions as AdminAIExecutions } from '@/pages/Admin/AIExecutions/AIExecutions';
import { AITraceDetail as AdminAITraceDetail } from '@/pages/Admin/AITraceDetail/AITraceDetail';
import { AIQuality as AdminAIQuality } from '@/pages/Admin/AIQuality/AIQuality';
import { AICostUsage as AdminAICostUsage } from '@/pages/Admin/AICostUsage/AICostUsage';
import { AICostBreakdown as AdminAICostBreakdown } from '@/pages/Admin/AICostBreakdown/AICostBreakdown';
import { AIKeyPool as AdminAIKeyPool } from '@/pages/Admin/AIKeyPool/AIKeyPool';
import { AdminSignIn } from '@/pages/Auth/AdminSignIn/AdminSignIn';
import { AuthenticationRequired } from '@/pages/Auth/AuthenticationRequired/AuthenticationRequired';
import { ForbiddenPage } from '@/pages/Forbidden/ForbiddenPage';
import { AccountStatus } from '@/pages/AccountStatus/AccountStatus';
import { NotFound } from '@/pages/NotFound/NotFound';
import { AuthRoute } from '@/auth/AuthRoute';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { DEFAULT_MENTOR_DESTINATION, DEFAULT_ADMIN_DESTINATION } from '@/auth/returnTo';

/**
 * GrowFlow Application Router
 *
 * Architecture model:
 * RootLayout (global AuthProvider + ScrollToTop)
 *   ├── AuthenticatedLayout (Student BUILD workspace: AuthHeader + Sidebar + Viewport)
 *   │     ├── /student/dashboard
 *   │     ├── /student/projects
 *   │     └── /student/projects/new
 *   └── PublicLayout (Public website & auth entry: Public Header + Outlet + Footer)
 *         ├── /
 *         ├── /features
 *         ├── /documentation
 *         ├── /contact
 *         ├── /showcase
 *         ├── /auth/student/*
 *         ├── /auth/mentor/*
 *         └── /mentor/overview
 */
export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      // 1. Authenticated Student BUILD Workspace
      {
        element: (
          <ProtectedRoute requiredRole="STUDENT">
            <AuthenticatedLayout />
          </ProtectedRoute>
        ),
        children: [
          {
            path: '/student/dashboard',
            element: <StudentDashboard />,
          },
          {
            path: '/student/projects',
            element: <StudentProjects />,
          },
          {
            path: '/student/projects/new',
            element: <StudentProjectCreate />,
          },
          {
            path: '/student/projects/mentor-catalog',
            element: <StudentMentorProjectCatalog />,
          },
          {
            path: '/student/projects/mentor-catalog/:definitionId',
            element: <StudentMentorProjectDetail />,
          },
          {
            path: '/student/projects/:projectId',
            element: <StudentProjectOverview />,
          },
          {
            path: '/student/projects/:projectId/overview',
            element: <StudentProjectOverview />,
          },
          {
            path: '/student/projects/:projectId/profile',
            element: <StudentProjectProfile />,
          },
          {
            path: '/student/projects/:projectId/assessment',
            element: <StudentAssessment />,
          },
          {
            path: '/student/projects/:projectId/blueprint',
            element: <StudentBlueprint />,
          },
          {
            path: '/student/projects/:projectId/blueprint/workspace',
            element: <StudentBlueprintWorkspace />,
          },
          {
            path: '/student/projects/:projectId/blueprint/documents',
            element: <StudentBlueprintDocumentViewer />,
          },
          {
            path: '/student/projects/:projectId/blueprint/documents/:documentKey',
            element: <StudentBlueprintDocumentViewer />,
          },
          {
            path: '/student/projects/:projectId/tasks',
            element: <StudentTasks />,
          },
          {
            path: '/student/projects/:projectId/tasks/:taskId',
            element: <StudentTaskDetail />,
          },
          {
            path: '/student/projects/:projectId/milestones',
            element: <StudentMilestones />,
          },
          {
            path: '/student/projects/:projectId/milestones/:milestoneId',
            element: <StudentMilestoneDetail />,
          },
          {
            path: '/student/projects/:projectId/risks',
            element: <StudentRisks />,
          },
          {
            path: '/student/projects/:projectId/risks/:riskId',
            element: <StudentRiskDetail />,
          },
          {
            path: '/student/projects/:projectId/roadmap',
            element: <StudentRoadmap />,
          },
          {
            path: '/student/projects/:projectId/documents',
            element: <StudentDocuments />,
          },
          {
            path: '/student/projects/:projectId/documents/:documentId',
            element: <StudentDocumentDetail />,
          },
          {
            path: '/student/projects/:projectId/github',
            element: <StudentGitHub />,
          },
          {
            path: '/student/projects/:projectId/activity',
            element: <StudentActivity />,
          },
          {
            path: '/student/projects/:projectId/ai-mentor',
            element: <StudentAIMentor />,
          },
          {
            path: '/student/projects/:projectId/help-requests',
            element: <StudentHelpRequests />,
          },
          {
            path: '/student/projects/:projectId/mentor-feedback',
            element: <StudentMentorFeedback />,
          },
          {
            path: '/student/projects/:projectId/changes',
            element: <StudentProjectChanges />,
          },
          {
            path: '/student/projects/:projectId/changes/:changeId',
            element: <StudentProjectChangeDetail />,
          },
          {
            path: '/student/groups',
            element: <StudentGroups />,
          },
          {
            path: '/profile',
            element: <StudentProfilePage />,
          },
          {
            path: '/settings',
            element: <StudentSettingsPage />,
          },
        ],
      },

      // 2. Authenticated Mentor SUPERVISE Workspace
      {
        element: (
          <ProtectedRoute requiredRole="MENTOR" loginPath="/auth/mentor/sign-in">
            <MentorLayout />
          </ProtectedRoute>
        ),
        children: [
          {
            path: '/mentor/overview',
            element: <MentorOverview />,
          },
          {
            path: '/mentor/groups',
            element: <GroupsDirectory />,
          },
          {
            path: '/mentor/groups/new',
            element: <GroupCreate />,
          },
          {
            path: '/mentor/groups/:groupId',
            element: <GroupWorkspace />,
          },
          {
            path: '/mentor/groups/:groupId/students',
            element: <GroupStudents />,
          },
          {
            path: '/mentor/groups/:groupId/projects',
            element: <GroupProjects />,
          },
          {
            path: '/mentor/groups/:groupId/at-risk',
            element: <GroupAtRisk />,
          },
          {
            path: '/mentor/groups/:groupId/activity',
            element: <GroupActivity />,
          },
          {
            path: '/mentor/groups/:groupId/ai',
            element: <GroupAIMentor />,
          },
          {
            path: '/mentor/projects',
            element: <ProjectsDirectory />,
          },
          {
            path: '/mentor/projects/new',
            element: <DefinitionCreate />,
          },
          {
            path: '/mentor/projects/instances',
            element: <MentorProjectsDirectory />,
          },
          {
            path: '/mentor/projects/:definitionId',
            element: <DefinitionDetail />,
          },
          {
            path: '/mentor/projects/:definitionId/edit',
            element: <DefinitionEdit />,
          },
          {
            path: '/mentor/projects/:definitionId/assign',
            element: <DefinitionAssign />,
          },
          {
            path: '/mentor/students',
            element: <StudentsDirectory />,
          },
          {
            path: '/mentor/students/:studentId',
            element: <StudentDetail />,
          },
          {
            path: '/mentor/students/:studentId/projects',
            element: <MentorStudentProjects />,
          },
          {
            path: '/mentor/students/:studentId/activity',
            element: <MentorStudentActivity />,
          },
          {
            path: '/mentor/project-instances',
            element: <ProjectInstances />,
          },
          {
            path: '/mentor/project-instances/:projectId',
            element: <ProjectInstanceDetail />,
          },
          {
            path: '/mentor/project-instances/:projectId/blueprint',
            element: <MentorInstanceBlueprint />,
          },
          {
            path: '/mentor/project-instances/:projectId/tasks',
            element: <MentorInstanceTasks />,
          },
          {
            path: '/mentor/project-instances/:projectId/milestones',
            element: <MentorInstanceMilestones />,
          },
          {
            path: '/mentor/project-instances/:projectId/risks',
            element: <MentorInstanceRisks />,
          },
          {
            path: '/mentor/project-instances/:projectId/documents',
            element: <MentorInstanceDocuments />,
          },
          {
            path: '/mentor/project-instances/:projectId/github',
            element: <MentorInstanceGitHub />,
          },
          {
            path: '/mentor/project-instances/:projectId/activity',
            element: <MentorInstanceActivity />,
          },
          {
            path: '/mentor/project-instances/:projectId/notes',
            element: <MentorInstanceNotes />,
          },
          {
            path: '/mentor/help-requests',
            element: <MentorHelpRequests />,
          },
          {
            path: '/mentor/at-risk',
            element: <AtRiskDirectory />,
          },
          {
            path: '/mentor/at-risk/:projectId',
            element: <AtRiskDetail />,
          },
          {
            path: '/mentor/activity',
            element: <MentorActivity />,
          },
          {
            path: '/mentor/ai',
            element: <MentorAI />,
          },
          {
            path: '/mentor/profile',
            element: <MentorProfile />,
          },
          {
            path: '/mentor/settings',
            element: <MentorSettings />,
          },
        ],
      },

      // 3. Authenticated Admin GOVERN Workspace
      {
        element: (
          <ProtectedRoute requiredRole="ADMIN" loginPath="/auth/admin/sign-in">
            <AdminLayout />
          </ProtectedRoute>
        ),
        children: [
          {
            path: '/admin/overview',
            element: <AdminOverview />,
          },
          {
            path: '/admin/mentors',
            element: <MentorDirectory />,
          },
          {
            path: '/admin/mentors/:mentorId',
            element: <AdminMentorDetail />,
          },
          {
            path: '/admin/students',
            element: <AdminStudentDirectory />,
          },
          {
            path: '/admin/students/:studentId',
            element: <AdminStudentDetail />,
          },
          {
            path: '/admin/groups',
            element: <AdminGroupsDirectory />,
          },
          {
            path: '/admin/groups/:groupId',
            element: <AdminGroupDetail />,
          },
          {
            path: '/admin/projects',
            element: <AdminProjectsDirectory />,
          },
          {
            path: '/admin/definitions',
            element: <AdminDefinitionsMonitoring />,
          },
          {
            path: '/admin/instances',
            element: <AdminInstancesMonitoring />,
          },
          {
            path: '/admin/instances/:projectId',
            element: <AdminInstanceDetail />,
          },
          {
            path: '/admin/ai',
            element: <AdminAIObservatory />,
          },
          {
            path: '/admin/ai/usage',
            element: <AdminAIUsage />,
          },
          {
            path: '/admin/ai/executions',
            element: <AdminAIExecutions />,
          },
          {
            path: '/admin/ai/executions/:executionId',
            element: <AdminAITraceDetail />,
          },
          {
            path: '/admin/ai/quality',
            element: <AdminAIQuality />,
          },
          {
            path: '/admin/ai/cost',
            element: <AdminAICostUsage />,
          },
          {
            path: '/admin/ai/cost/:dimension',
            element: <AdminAICostBreakdown />,
          },
          {
            path: '/admin/ai/keys',
            element: <AdminAIKeyPool />,
          },
          {
            path: '/admin/system-health',
            element: <AdminSystemHealth />,
          },
          {
            path: '/admin/system-health/:component',
            element: <AdminComponentDetail />,
          },
          {
            path: '/admin/security',
            element: <AdminSecurityOverview />,
          },
          {
            path: '/admin/security/audit',
            element: <AdminAuditLog />,
          },
          {
            path: '/admin/security/investigations',
            element: <AdminInvestigationRequests />,
          },
          {
            path: '/admin/security/investigations/:investigationId',
            element: <AdminInvestigationDetail />,
          },
          {
            path: '/admin/documents',
            element: <AdminDocumentsRAG />,
          },
          {
            path: '/admin/documents/rag',
            element: <AdminRAGMonitoring />,
          },
          {
            path: '/admin/documents/generation',
            element: <AdminDocumentGeneration />,
          },
          {
            path: '/admin/analytics',
            element: <AdminPlatformAnalytics />,
          },
          {
            path: '/admin/analytics/:dimension',
            element: <AdminAnalyticsDetail />,
          },
          {
            path: '/admin/profile',
            element: <AdminProfile />,
          },
          {
            path: '/admin/settings',
            element: <AdminSettings />,
          },
        ],
      },

      // 4. Public Website & Authentication Entry Points
      {
        element: <PublicLayout />,
        children: [
          {
            path: '/',
            element: <Landing />,
          },
          {
            path: '/features',
            element: <Features />,
          },
          {
            path: '/documentation',
            element: <Documentation />,
          },
          {
            path: '/contact',
            element: <Contact />,
          },
          {
            path: '/showcase',
            element: <Showcase />,
          },
          {
            path: '/auth/student/sign-in',
            element: (
              <AuthRoute>
                <StudentSignIn />
              </AuthRoute>
            ),
          },
          {
            path: '/auth/student/register',
            element: (
              <AuthRoute>
                <StudentRegister />
              </AuthRoute>
            ),
          },
          {
            path: '/auth/student/recover',
            element: (
              <AuthRoute>
                <StudentPasswordRecovery />
              </AuthRoute>
            ),
          },
          {
            path: '/auth/mentor/sign-in',
            element: (
              <AuthRoute defaultDestination={DEFAULT_MENTOR_DESTINATION}>
                <MentorSignIn />
              </AuthRoute>
            ),
          },
          {
            path: '/auth/mentor/register',
            element: (
              <AuthRoute defaultDestination={DEFAULT_MENTOR_DESTINATION}>
                <MentorRegister />
              </AuthRoute>
            ),
          },
          {
            path: '/auth/mentor/recover',
            element: (
              <AuthRoute defaultDestination={DEFAULT_MENTOR_DESTINATION}>
                <MentorPasswordRecovery />
              </AuthRoute>
            ),
          },
          {
            path: '/auth/admin/sign-in',
            element: (
              <AuthRoute defaultDestination={DEFAULT_ADMIN_DESTINATION}>
                <AdminSignIn />
              </AuthRoute>
            ),
          },
          {
            path: '/401',
            element: <AuthenticationRequired />,
          },
          {
            path: '/403',
            element: <ForbiddenPage />,
          },
          {
            path: '/account-status',
            element: <AccountStatus />,
          },
          {
            path: '/404',
            element: <NotFound />,
          },
          {
            path: '*',
            element: <NotFound />,
          },
        ],
      },
    ],
  },
]);

