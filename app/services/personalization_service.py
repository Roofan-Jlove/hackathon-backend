from typing import Optional, List
from app.models import UserProfile


class PersonalizationService:
    """Service for content personalization based on user profile."""

    @staticmethod
    def get_complexity_level(profile: Optional[UserProfile]) -> str:
        """
        Determine content complexity level based on user profile.

        Args:
            profile: User profile (can be None for anonymous users)

        Returns:
            Complexity level: 'beginner', 'intermediate', or 'advanced'
        """
        if not profile:
            return 'intermediate'  # Default for anonymous users

        # Calculate complexity based on multiple factors
        scores = {
            'beginner': 0,
            'intermediate': 0,
            'advanced': 0
        }

        # Programming experience
        prog_exp_map = {
            'beginner': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced',
            'expert': 'advanced'
        }
        if profile.programming_experience:
            scores[prog_exp_map.get(profile.programming_experience, 'intermediate')] += 2

        # Python proficiency
        python_map = {
            'never': 'beginner',
            'basic': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced'
        }
        if profile.python_proficiency:
            scores[python_map.get(profile.python_proficiency, 'intermediate')] += 2

        # ROS experience (weighted higher since it's core to the course)
        ros_map = {
            'never_heard': 'beginner',
            'heard': 'beginner',
            'beginner': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced'
        }
        if profile.ros_experience:
            scores[ros_map.get(profile.ros_experience, 'beginner')] += 3

        # AI/ML experience
        ai_map = {
            'none': 'beginner',
            'theoretical': 'beginner',
            'pretrained': 'intermediate',
            'custom': 'advanced',
            'production': 'advanced'
        }
        if profile.ai_ml_experience:
            scores[ai_map.get(profile.ai_ml_experience, 'intermediate')] += 2

        # Return the level with highest score
        return max(scores, key=scores.get)

    @staticmethod
    def should_show_prerequisites(profile: Optional[UserProfile]) -> bool:
        """
        Determine if prerequisite sections should be shown.

        Args:
            profile: User profile

        Returns:
            True if prerequisites should be shown
        """
        if not profile:
            return True  # Show prerequisites for anonymous users

        # Show prerequisites if user is beginner in programming or Python
        if profile.programming_experience in ['beginner', None]:
            return True
        if profile.python_proficiency in ['never', 'basic', None]:
            return True

        return False

    @staticmethod
    def get_recommended_topics(profile: Optional[UserProfile]) -> List[str]:
        """
        Get recommended topics based on user interests and background.

        Args:
            profile: User profile

        Returns:
            List of recommended topic IDs
        """
        if not profile or not profile.primary_interests:
            return []

        # Map interests to specific content sections
        interest_mapping = {
            'autonomous_navigation': ['week-4', 'week-5', 'week-7'],
            'computer_vision': ['week-8', 'week-10', 'week-11'],
            'manipulation': ['week-6', 'week-9'],
            'human_robot_interaction': ['week-11', 'week-12'],
            'simulation': ['week-4', 'week-5'],
            'physical_ai': ['week-10', 'week-11', 'week-12']
        }

        recommended = []
        for interest in profile.primary_interests:
            recommended.extend(interest_mapping.get(interest, []))

        # Remove duplicates while preserving order
        return list(dict.fromkeys(recommended))

    @staticmethod
    def get_personalization_context(profile: Optional[UserProfile]) -> str:
        """
        Generate a context string for personalized RAG prompts.

        Args:
            profile: User profile

        Returns:
            Context string describing user's background
        """
        if not profile:
            return "The user is new to the topic."

        context_parts = []

        # Programming background
        if profile.programming_experience:
            context_parts.append(f"Programming experience: {profile.programming_experience}")

        if profile.python_proficiency:
            context_parts.append(f"Python proficiency: {profile.python_proficiency}")

        # ROS background
        if profile.ros_experience:
            if profile.ros_experience in ['never_heard', 'heard']:
                context_parts.append("New to ROS")
            else:
                context_parts.append(f"ROS experience: {profile.ros_experience}")

        # AI/ML background
        if profile.ai_ml_experience:
            context_parts.append(f"AI/ML experience: {profile.ai_ml_experience}")

        # Hardware background
        if profile.robotics_hardware_experience:
            context_parts.append(f"Hardware experience: {profile.robotics_hardware_experience}")

        # Learning goals
        if profile.primary_interests:
            interests = ", ".join(profile.primary_interests)
            context_parts.append(f"Interested in: {interests}")

        return ". ".join(context_parts) + "."

    @staticmethod
    def get_learning_style(profile: Optional[UserProfile]) -> str:
        """
        Determine preferred learning style based on profile.

        Args:
            profile: User profile

        Returns:
            Learning style: 'theory_focused', 'practical_focused', or 'balanced'
        """
        if not profile:
            return 'balanced'

        # Theory-focused if strong AI/ML background
        if profile.ai_ml_experience in ['research', 'custom', 'production']:
            return 'theory_focused'

        # Practical-focused if strong hardware background
        if profile.robotics_hardware_experience in ['industrial', 'research']:
            return 'practical_focused'

        return 'balanced'
