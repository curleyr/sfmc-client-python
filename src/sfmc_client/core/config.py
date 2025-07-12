# --- core/config.py ---
from __future__ import annotations
import os
import json
from typing import Optional, MutableMapping


from dotenv import load_dotenv
load_dotenv()

class Config:
    def __init__(
        self,
        account_name: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        account_id: Optional[str] = None,
        tenant_subdomain: Optional[str] = None,
        environment: Optional[MutableMapping[str, str]] = None
    ) -> None:
        """
        Load and store Salesforce Marketing Cloud configuration.

        Attempts to load config from parameters, falling back to environment variables.

        :param account_name: Logical key to map to an account ID using SFMC_ACCOUNT_IDS (optional).
        :param client_id: OAuth client ID (optional).
        :param client_secret: OAuth client secret (optional).
        :param account_id: SFMC MID/account ID. Optional if account_name and SFMC_ACCOUNT_IDS are used.
        :param tenant_subdomain: Subdomain for SFMC API endpoints (e.g., "mctest").
        :param environment: Optional mapping to override environment variables (e.g., for testing).
        :raises ValueError: If required fields are missing or malformed.
        """
        self.env = environment or os.environ

        self.client_id = client_id or self.env.get("SFMC_CLIENT_ID", "")
        self.client_secret = client_secret or self.env.get("SFMC_CLIENT_SECRET", "")
        self.tenant_subdomain = tenant_subdomain or self.env.get("SFMC_TENANT_SUBDOMAIN", "")
        self.account_ids = self._load_account_ids()
        self.account_name = account_name or self._get_default_account_name()
        self.account_id = account_id or self._resolve_account_id()

        self._validate()

    def _load_account_ids(self) -> dict:
        """
        Load account IDs from the SFMC_ACCOUNT_IDS environment variable (JSON string).

        :return: Dictionary of {account_name: account_id}.
        :raises ValueError: If the variable is not valid JSON.
        """
        ids = self.env.get("SFMC_ACCOUNT_IDS", "{}")
        try:
            return json.loads(ids)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in SFMC_ACCOUNT_IDS")

    def _get_default_account_name(self) -> Optional[str]:
        """
        Get the first key from the account ID mapping if no account name was provided.

        :return: First account name, or None if no mapping exists.
        """
        if not self.account_ids:
            return None
        return next(iter(self.account_ids))

    def _resolve_account_id(self) -> Optional[str]:
        """
        Resolve the account ID from the account name or fallback to SFMC_ACCOUNT_ID.

        :return: The resolved account ID.
        """
        if self.account_name and self.account_name in self.account_ids:
            return self.account_ids[self.account_name]
        return self.env.get("SFMC_ACCOUNT_ID")  # fallback

    def _validate(self) -> None:
        """
        Ensure that all required configuration values are set.

        :raises ValueError: If any required values are missing or unresolved.
        """
        if not self.client_id:
            raise ValueError("Missing SFMC_CLIENT_ID")
        if not self.client_secret:
            raise ValueError("Missing SFMC_CLIENT_SECRET")
        if not self.tenant_subdomain:
            raise ValueError("Missing SFMC_TENANT_SUBDOMAIN")
        if not self.account_id:
            raise ValueError(f"Unable to resolve account_id for account_name: {self.account_name}")
