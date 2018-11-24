# -*- coding: utf-8 -*-
from examples.framework import (
    SimpleUseCase,
    UseCaseInput,
)
from examples.framework.dependency_injection import Inject

from . import entities, repos, services


class InvitateUserInput(UseCaseInput):
    # TODO decide:
    # - do use-case DTOs have unstructured `data` dict
    # - or do they inherit and add explicite, named fields
    #   but then their description is redundant to the
    #   schema definition
    email: entities.Email


class InvitateUser(SimpleUseCase):

    Input = InvitateUserInput

    def is_available(self, data: InvitateUserInput):
        user_repo = repos.UserRepo(self.container)
        return not user_repo.is_email_taken(data.email)


class AcceptInvitation(SimpleUseCase):

    user_repo: repos.UserRepo = Inject()
    invitation_repo: repos.InvitationRepo = Inject()

    class Input(UseCaseInput):
        email: entities.Email
        token: entities.InvitationToken

    def is_available(self, data: Input):
        invitation = self.invitation_repo.get_by_token(data.token)
        return (
            not self.user_repo.is_email_taken(data.email) and
            services.is_invitation_valid(invitation, data.email)
        )
