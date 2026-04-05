# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in REDROOM, please email security@redroom-project.local instead of using the GitHub issue tracker.

**Do not** open public GitHub issues for security vulnerabilities.

Include in your report:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if applicable)

You will receive an acknowledgment within 48 hours and a more detailed response within 5 business days.

## Security Considerations

### Data Sensitivity

REDROOM processes forensic evidence which may be sensitive. When deploying:

1. **Network Security**
   - Run within air-gapped networks when processing classified evidence
   - Use VPNs or private networks for remote deployments
   - Implement network policies to restrict access

2. **Storage Security**
   - Use encrypted volumes for evidence storage
   - Limit ledger database access to authorized users
   - Implement regular backups with encryption
   - Consider data at-rest encryption

3. **Access Control**
   - Use multi-factor authentication for API access
   - Implement role-based access control (RBAC)
   - Log all analyst access to the ledger
   - Restrict remote access when possible

4. **Credentials Management**
   - Never commit credentials to Git
   - Use environment variables or secret managers
   - Rotate credentials regularly
   - Audit credential usage

### Deployment Security

- Run containers with non-root users (already configured)
- Use security scanning tools before deployment
- Keep base images updated regularly
- Implement Pod Security Policies in Kubernetes
- Use NetworkPolicies to restrict traffic

### API Security

- All API endpoints should run over HTTPS in production
- Implement rate limiting to prevent abuse
- Use API authentication tokens
- Log all API requests
- Monitor for suspicious patterns

## Vulnerability Scanning

Before each release, run:

```bash
# Python dependency scanning
pip install safety
safety check

# Container image scanning
docker scan redroom:latest

# SAST scanning
pip install bandit
bandit -r redroom/
```

## Supported Versions

| Version | Supported | EOL Date |
|---------|-----------|----------|
| 1.0.x   | Yes       | TBD      |

## Dependencies

REDROOM uses the following key dependencies:
- FastAPI - API framework
- OpenCV - Computer vision
- NumPy/SciPy - Numerical analysis
- SQLAlchemy - Database ORM
- Pydantic - Data validation

All dependencies are pinned to specific versions in requirements.txt for reproducibility.

## Known Issues

None currently known. Report security issues privately as described above.

## Best Practices

When deploying REDROOM:

1. Run latest version of all components
2. Use encrypted storage for evidence
3. Implement strong authentication
4. Monitor logs for anomalies
5. Regular security audits
6. Restricted network access
7. Encrypted communication channels
8. Regular backup and recovery testing

## Contact

For security inquiries: security@redroom-project.local

For general questions: issues@redroom-project.local

---

Last updated: 2026-04-06
