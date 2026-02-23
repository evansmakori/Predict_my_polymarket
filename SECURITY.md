# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of our project seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** open a public issue
2. Email the maintainers directly (add your email here)
3. Include detailed information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment within 48 hours
- Status update within 7 days
- Fix timeline based on severity

## Security Best Practices

### For Deployment

1. **Environment Variables**
   - Never commit `.env` files
   - Use secure secret management (AWS Secrets Manager, Vault, etc.)
   - Rotate API keys regularly

2. **Database**
   - Keep DuckDB files out of version control
   - Regular backups
   - Access control in production

3. **API Security**
   - Enable CORS only for trusted domains
   - Implement rate limiting
   - Use HTTPS in production
   - Add authentication/authorization if handling sensitive data

4. **Dependencies**
   - Regularly update dependencies
   - Use `pip audit` and `npm audit`
   - Review security advisories

### For Development

1. **Code Review**
   - All PRs require review
   - Security-focused code review checklist

2. **Testing**
   - Include security tests
   - Input validation tests
   - Authentication/authorization tests (when implemented)

## Known Security Considerations

### Current Implementation

- **No Authentication**: This is a data analytics tool without built-in auth
  - Add authentication before exposing to the internet
  - Consider API keys or OAuth for production

- **Public APIs**: Uses public Polymarket APIs
  - No sensitive user data collected
  - Rate limiting recommended

- **Database**: Local DuckDB
  - Secure file permissions in production
  - Consider encryption at rest for sensitive deployments

### Recommendations for Production

1. Add authentication middleware (e.g., Auth0, Firebase Auth)
2. Implement API rate limiting
3. Use HTTPS/TLS certificates
4. Set up monitoring and alerting
5. Regular security audits
6. Implement CSRF protection if adding write operations
7. Add input sanitization for user-provided URLs

## Compliance

This project:
- Does not collect personal user data
- Uses public market data only
- Stores analytical data locally

If deploying in a regulated environment:
- Review data handling requirements
- Implement appropriate controls
- Add audit logging
- Consider data retention policies

## Updates

This security policy is reviewed quarterly and updated as needed.

Last updated: 2026-02-23
