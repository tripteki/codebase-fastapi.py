import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.app.routes.app_ws_router import getSocketIOServer
from src.v1.api.log.support.admin_refresh_broadcaster import AdminRefreshBroadcaster
from src.v1.api.user.listeners.user_admin_activated_broadcast_listener import handleUserAdminActivatedBroadcast
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository


class TestTransfer:
    """Import, export, and realtime payloads shared with Nest."""

    @pytest.mark.asyncio
    async def test_import_export_and_realtime (self, client: AsyncClient, auth_token: str, test_user: dict) -> None:
        """
        Import and export responses, socket payloads, and CSV columns.
        """
        captured = []
        server = getSocketIOServer ()

        async def spy (event, data=None, room=None, **kwargs):
            captured.append ({
                "event": event,
                "payload": data,
                "room": room,
            })

        server.emit = spy

        email = f"transfer-{test_user ['id'][-6:].lower ()}-fa@test.com"
        name = f"Transfer {email.split ('@') [0]}"
        csvContent = f"name,email,password,status\n{name},{email},password123,active\n".encode ()
        response = await client.post (
            "/api/v1/admin/users/import",
            headers={"Authorization": f"Bearer {auth_token}"},
            files={"file": ("users.csv", csvContent, "text/csv")},
        )

        assert response.status_code == 200
        assert response.json () == "Import started"

        imported = [item for item in captured if item ["event"] == "v1.user.admin.imported"]
        assert imported
        assert set (imported [-1] ["payload"]) == {"userId", "filename", "totalImported", "totalSkipped"}
        assert imported [-1] ["room"] == f"user:{test_user ['id']}"
        assert imported [-1] ["payload"] ["totalImported"] + imported [-1] ["payload"] ["totalSkipped"] == 1

        created = [item for item in captured if item ["event"] == "v1.notification.created"]
        assert created
        assert set (created [-1] ["payload"]) == {"id", "unread"}

        captured.clear ()
        response = await client.post (
            "/api/v1/admin/users/export?export_type=csv",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        assert response.json () == "Export started"

        exported = [item for item in captured if item ["event"] == "v1.user.admin.exported"]
        assert exported
        assert set (exported [-1] ["payload"]) == {"userId", "filename", "fileUrl"}
        filename = exported [-1] ["payload"] ["filename"]
        assert filename.startswith ("users_export_")
        assert filename.endswith (".csv")

        exportPath = Path ("storage/disks/public/export") / filename
        header = exportPath.read_text ().splitlines () [0]
        assert header == "full_name,email,role,status,created_at"
        sample = next (line for line in exportPath.read_text ().splitlines () [1:] if email in line)
        fullName, sampleEmail, role, status, _createdAt = sample.split (",")
        assert fullName == name
        assert sampleEmail == email
        assert role == "user"
        assert status == "active"

        captured.clear ()

        async def otherUsers (_names, _roles):
            return ["other-user"]

        with patch.object (UserAclRepository, "findUserIdsByPermissionNames", staticmethod (otherUsers)):
            await AdminRefreshBroadcaster.broadcast (["users"], test_user ["id"])
        refresh = captured [-1]
        assert refresh ["event"] == "v1.admin.refresh"
        assert refresh ["room"] == "user:other-user"
        assert refresh ["payload"] == {"userId": "other-user", "scopes": ["users"]}

        captured.clear ()
        moment = datetime (2026, 1, 2, 3, 4, 5)
        await handleUserAdminActivatedBroadcast (SimpleNamespace (
            id="account-1",
            name="Ada",
            email="ada@test.com",
            password="secret",
            email_verified_at=moment,
            created_at=moment,
            updated_at=moment,
            deleted_at=None,
        ))
        activated = captured [-1]
        assert activated ["event"] == "v1.user.admin.activated"
        assert activated ["room"] == "user:account-1"
        assert "password" not in activated ["payload"]
        assert activated ["payload"] ["email_verified_at"] == "2026-01-02 03:04:05"
        assert set (activated ["payload"]) == {
            "id", "name", "email", "email_verified_at", "created_at", "updated_at", "deleted_at",
        }

        login = await client.post (
            "/api/v1/auth/login",
            json={
                "identifierKey": "email",
                "identifierValue": test_user ["email"],
                "password": test_user ["password"],
                "remember": True,
            },
        )
        assert login.status_code == 201
        loginKeys = sorted (login.json ().keys ())
        assert loginKeys == ["accessToken", "accessTokenTtl", "refreshToken", "refreshTokenTtl"]

        listing = await client.get (
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert listing.status_code == 200
        pageKeys = sorted (listing.json ().keys ())
        assert pageKeys == [
            "currentPage", "data", "firstPage", "lastPage", "nextPage", "perPage", "previousPage", "total", "totalPage",
        ]

        captured.clear ()
        roleName = f"transfer-role-{test_user ['id'][-4:].lower ()}"
        roleResponse = await client.post (
            "/api/v1/admin/roles/import",
            headers={"Authorization": f"Bearer {auth_token}"},
            files={"file": ("roles.csv", f"name,guard_name,permissions\n{roleName},web,user.view\n".encode (), "text/csv")},
        )
        assert roleResponse.status_code == 200
        assert roleResponse.json () == "Import started"
        roleImported = [item for item in captured if item ["event"] == "v1.acl.role.admin.imported"] [-1]
        assert set (roleImported ["payload"]) == {"userId", "filename", "totalImported", "totalSkipped"}
        assert roleImported ["room"] == f"user:{test_user ['id']}"

        captured.clear ()
        roleExport = await client.post (
            "/api/v1/admin/roles/export?export_type=csv",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert roleExport.status_code == 200
        assert roleExport.json () == "Export started"
        roleExported = [item for item in captured if item ["event"] == "v1.acl.role.admin.exported"] [-1]
        assert set (roleExported ["payload"]) == {"userId", "filename", "fileUrl"}
        roleFile = roleExported ["payload"] ["filename"]
        assert roleFile.startswith ("roles_export_") and roleFile.endswith (".csv")
        roleHeader = (Path ("storage/disks/public/export") / roleFile).read_text ().splitlines () [0]
        assert roleHeader == "name,guard_name,permissions"

        captured.clear ()
        permissionName = f"transfer.permission.{test_user ['id'][-4:].lower ()}"
        permissionResponse = await client.post (
            "/api/v1/admin/permissions/import",
            headers={"Authorization": f"Bearer {auth_token}"},
            files={"file": ("permissions.csv", f"name,guard_name\n{permissionName},web\n".encode (), "text/csv")},
        )
        assert permissionResponse.status_code == 200
        assert permissionResponse.json () == "Import started"
        permissionImported = [item for item in captured if item ["event"] == "v1.acl.permission.admin.imported"] [-1]
        assert set (permissionImported ["payload"]) == {"userId", "filename", "totalImported", "totalSkipped"}

        captured.clear ()
        permissionExport = await client.post (
            "/api/v1/admin/permissions/export?export_type=csv",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert permissionExport.status_code == 200
        assert permissionExport.json () == "Export started"
        permissionExported = [item for item in captured if item ["event"] == "v1.acl.permission.admin.exported"] [-1]
        assert set (permissionExported ["payload"]) == {"userId", "filename", "fileUrl"}
        permissionFile = permissionExported ["payload"] ["filename"]
        assert permissionFile.startswith ("permissions_export_") and permissionFile.endswith (".csv")
        permissionHeader = (Path ("storage/disks/public/export") / permissionFile).read_text ().splitlines () [0]
        assert permissionHeader == "name,guard_name"

        Path ("/tmp/codebase-transfer-fastapi.json").write_text (json.dumps ({
            "importMessage": "Import started",
            "exportMessage": "Export started",
            "importKeys": sorted (["userId", "filename", "totalImported", "totalSkipped"]),
            "exportKeys": sorted (["userId", "filename", "fileUrl"]),
            "refresh": {"userId": "other-user", "scopes": ["users"], "room": "user:other-user"},
            "notificationKeys": sorted (["id", "unread"]),
            "csvHeader": header,
            "sample": {"role": role, "status": status},
            "activatedAt": activated ["payload"] ["email_verified_at"],
            "filenamePattern": "users_export_YYYYMMDD_HHMMSS.csv",
            "loginKeys": loginKeys,
            "pageKeys": pageKeys,
            "roleCsvHeader": roleHeader,
            "permissionCsvHeader": permissionHeader,
            "aclSockets": [
                "v1.acl.permission.admin.exported",
                "v1.acl.permission.admin.imported",
                "v1.acl.role.admin.exported",
                "v1.acl.role.admin.imported",
            ],
        }, indent=2))
