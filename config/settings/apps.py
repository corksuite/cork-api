
# ==============================================================================
# DJANGO Domain
# ==============================================================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# ==============================================================================
# THIRD PARTY Domain
# ==============================================================================

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # "drf_spectacular",
    "corsheaders",
]

# ==============================================================================
# CORE Domain
# ==============================================================================

CORE_APPS = [
    "apps.core.apps.CoreConfig",
]

# ==============================================================================
# IDENTITY Domain
# ==============================================================================

IDENTITY_APPS = [
    "apps.identity.authentication.apps.AuthenticationConfig",
    "apps.identity.users.apps.UsersConfig",
    "apps.identity.organizations.apps.OrganizationsConfig",
    "apps.identity.permissions.apps.PermissionsConfig",
]

# ==============================================================================
# Work Domain
# ==============================================================================

WORK_APPS = [
    "apps.work.projects.apps.ProjectsConfig",
    "apps.work.tasks.apps.TasksConfig",
    "apps.work.workflows.apps.WorkflowsConfig",
    "apps.work.scheduling.apps.SchedulingConfig",
    "apps.work.goals.apps.GoalsConfig",
]


# ==============================================================================
# Collaboration Domain
# ==============================================================================

COLLABORATION_APPS = [
    "apps.collaboration.messaging.apps.MessagingConfig",
    "apps.collaboration.channels.apps.ChannelsConfig",
    "apps.collaboration.meetings.apps.MeetingsConfig",
    "apps.collaboration.notifications.apps.NotificationsConfig",
    "apps.collaboration.presence.apps.PresenceConfig",
    "apps.collaboration.activity.apps.ActivityConfig",
]


# ==============================================================================
# Knowledge Domain
# ==============================================================================

KNOWLEDGE_APPS = [
    "apps.knowledge.documents.apps.DocumentsConfig",
    "apps.knowledge.assets.apps.AssetsConfig",
    "apps.knowledge.wiki.apps.WikiConfig",
    "apps.knowledge.search.apps.SearchConfig",
]


# ==============================================================================
# Intelligence Domain
# ==============================================================================

INTELLIGENCE_APPS = [
    "apps.intelligence.ai.apps.AIConfig",
    "apps.intelligence.automation.apps.AutomationConfig",
    "apps.intelligence.analytics.apps.AnalyticsConfig",
]


# ==============================================================================
# Local Apps
# ==============================================================================

LOCAL_APPS = (
    CORE_APPS
    + IDENTITY_APPS
    + WORK_APPS
    + COLLABORATION_APPS
    + KNOWLEDGE_APPS
    + INTELLIGENCE_APPS
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
