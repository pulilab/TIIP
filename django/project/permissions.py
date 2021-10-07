from rest_framework import permissions

from project.models import ProjectApproval, Portfolio, ReviewScore, ProjectPortfolioState


class InTeamOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow team members of a project to edit it.

    `obj` needs to be a `Project` instance
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        is_country_manager = False
        co_id = obj.get_country_office_id()
        if co_id:
            is_country_manager = request.user.userprofile.manager_of.filter(id=co_id).exists()

        return request.user.is_superuser or obj.team.filter(
            id=request.user.userprofile.id).exists() or is_country_manager


class InCountryAdminForApproval(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: ProjectApproval):
        if hasattr(obj.project, 'search') and hasattr(obj.project.search, 'country'):
            return request.user.is_superuser \
                   or obj.project.search.country.admins.filter(id=request.user.userprofile.id).exists() \
                   or obj.project.search.country.super_admins.filter(id=request.user.userprofile.id).exists()


class IsGPOOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow Global portfolio owners to create new portfolios
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # pragma: no cover
        return request.user.userprofile.global_portfolio_owner


class IsGPOOrManagerPortfolio(permissions.BasePermission):
    """
    GPOs and managers have full access to portfolios
    """

    def has_object_permission(self, request, view, obj: Portfolio):
        return request.user.userprofile.global_portfolio_owner or obj.managers.filter(id=request.user.userprofile.id)


class IsGPOOrManagerProjectPortfolioState(permissions.BasePermission):
    """
    GPOs and managers have full access to portfolios, others only read access
    """

    def has_object_permission(self, request, view, obj: ProjectPortfolioState):
        if request.method in permissions.SAFE_METHODS:
            return True  # pragma: no cover

        return request.user.userprofile.global_portfolio_owner or obj.portfolio.managers.filter(
            id=request.user.userprofile.id)


class IsReviewable(permissions.BasePermission):
    """
    Portfolio reviews can only be accessed by reviewers once
    """

    def has_object_permission(self, request, view, obj: ReviewScore):
        return obj.reviewer.id == request.user.userprofile.id and obj.status != ReviewScore.STATUS_COMPLETE


class IsReviewerGPOOrManager(permissions.BasePermission):
    """
    Portfolio review scores can only be seen by managers, assigned reviewers and GPO's
    Only GPO's can delete review scores.
    """

    def has_object_permission(self, request, view, obj: ReviewScore):
        # Read permissions are also allowed to assigned reviewers, so we'll allow GET, HEAD or OPTIONS requests.
        base_condition = request.user.userprofile.global_portfolio_owner or \
                         obj.portfolio_review.portfolio.managers.filter(id=request.user.userprofile.id)
        if request.method in permissions.SAFE_METHODS:
            return base_condition or \
                   obj.reviewer.id == request.user.userprofile.id
        return base_condition
