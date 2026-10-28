# IT Help Desk Lab

I built a Microsoft Entra ID tenant on my own domain and worked the tickets a Tier 1 help desk handles every week. That covers password resets, MFA setup, a lost phone, self-service password reset, and least-privilege admin roles. Every step has a screenshot.

The tenant runs on Entra ID Free with no Azure subscription attached, so nothing in it can generate a bill.

## What this lab shows

- Creating users and security groups in Microsoft Entra ID
- Adding and verifying a custom domain through DNS
- Admin password resets and forced password change at first sign-in
- MFA registration with Microsoft Authenticator under security defaults
- Recovering a user who lost their MFA phone (require re-registration)
- Self-service password reset (SSPR)
- Role-based access with the Helpdesk Administrator role, and proof of where that role stops
- Reading Entra licensing limits instead of assuming a feature works

## Environment

| Item | Value |
| --- | --- |
| Tenant | IT Help Desk Lab |
| Plan | Microsoft Entra ID Free |
| Custom domain | jomiranda.com (verified, primary) |
| DNS | Vercel |
| Daily admin | admin@jomiranda.com (Global Administrator) |
| MFA enforcement | Security defaults |

### Lab users

| User | Department | Job title | Role in the lab |
| --- | --- | --- | --- |
| alex.tech | IT | Help Desk Technician | Holds Helpdesk Administrator |
| maria.sales | Sales | Account Executive | Password reset and MFA setup |
| pedro.sales | Sales | Sales Representative | Lost-phone MFA recovery |
| ana.finance | Finance | Financial Analyst | Target of Alex's password reset |
| lucas.newhire | none yet | New Hire | Left without a department or group on purpose, for a later new-hire scenario |

### Groups

| Group | Type | Membership | Members |
| --- | --- | --- | --- |
| SG-Sales | Security | Assigned | Maria, Pedro |
| SG-IT-Support | Security | Assigned | Alex |

Both groups are assigned. Dynamic groups need Entra ID P1.

## Walkthrough

### 1. Tenant and custom domain

I renamed the default directory to IT Help Desk Lab, then added jomiranda.com. Entra gave me a TXT record (`MS=ms...`), I added it in Vercel DNS, and the domain verified within a few minutes. I set it as primary so new users default to `@jomiranda.com`.

![Tenant overview](screenshots/01-tenant-overview.png)
![Custom domain verified and primary](screenshots/02-domain-verified.png)

### 2. A separate admin account

The personal Microsoft account that created the tenant shows up inside it as an external account (its username contains `#EXT#`). I don't use it for daily work. I created `admin@jomiranda.com`, a native work account with Global Administrator, and did everything after this point from that account. The personal account stays as a backup way in. I hid it in the user list screenshot.

![Admin account with Global Administrator](screenshots/03-admin-account.png)
![Admin account overview](screenshots/03a-admin-overview.png)

### 3. Users and groups

Five users with department and job title filled in, plus two security groups.

![Users with department and job title](screenshots/04-users-created.png)
![Security groups](screenshots/05-groups.png)
![SG-Sales members](screenshots/06-sg-sales-members.png)

### 4. Ticket: "I forgot my password" (Maria)

As admin I reset Maria's password, which generates a temporary one. When she signed in with it, Entra forced her to set a new password before going any further.

![Admin password reset](screenshots/07-admin-password-reset.png)
![Forced password change at sign-in](screenshots/08-forced-password-change.png)

### 5. MFA under security defaults

Security defaults are on, so every user has to register MFA. Maria registered an authenticator app. Hers shows up as a TOTP code rather than a Microsoft Authenticator push notification. That difference matters on real tickets, because "approve the notification" means nothing to a user who only gets codes.

![Maria's MFA method](screenshots/09-mfa-registered.png)
![Security defaults enabled](screenshots/10-security-defaults.png)

### 6. Helpdesk Administrator and least privilege (Alex)

I gave Alex the Helpdesk Administrator role. He registered Microsoft Authenticator (push) and an alternate email.

![Alex's Helpdesk Administrator role](screenshots/11-alex-helpdesk-admin.png)
![Authenticator setup, QR code hidden](screenshots/12-mfa-qr-setup.png)
![Alex's sign-in methods](screenshots/12a-alex-security-info.png)

Then I signed in as Alex and tested the role from both sides. Resetting Ana's password worked, since she's a standard user.

![Alex resets Ana's password](screenshots/13-alex-resets-ana.png)

Resetting the Global Administrator's password failed with this message:

> The password can not be reset. This may be due to an incorrect level of administrative privilege or if trying to reset your own password.

That's the behavior I wanted to prove. A help desk role can unlock regular users without being able to take over an admin account.

![Alex blocked from resetting the admin](screenshots/14-alex-denied-admin.png)

### 7. Self-service password reset

Alex reset his own password at aka.ms/sspr using a code sent to his alternate email.

![SSPR verification](screenshots/15-sspr-verification.png)
![SSPR success](screenshots/16-sspr-success.png)

The SSPR policy page says admins are always enabled for SSPR and need two authentication methods. In my test Alex only had to pass one verification step. I'm recording what happened rather than what the banner says.

![SSPR policy page](screenshots/17-sspr-policy.png)

### 8. Ticket: "I got a new phone and can't sign in" (Pedro)

Pedro registered Microsoft Authenticator on his phone. Then I played out the common ticket where the old phone is gone. As admin I used Require re-register multifactor authentication on his account. His registered methods dropped to "No usable methods", so his next sign-in makes him set up MFA again on the new phone.

![Pedro's original MFA registration](screenshots/18-pedro-mfa-registered.png)
![MFA re-registration required](screenshots/19-require-mfa-reregister.png)

## Licensing notes

This lab runs on Entra ID Free, and that shaped a few decisions.

- SSPR for regular users requires Entra ID P1 (or Microsoft 365 Business Standard and up). The portal still lets you switch it on for users on Free, but the license doesn't cover it, so I left it off and demonstrated SSPR with an admin account, which Free does cover.
- Dynamic groups and Conditional Access also need P1, so this lab uses assigned groups and security defaults.
- I tried the free P2 trial. With a Brazil billing address, checkout asks for a CNPJ (a Brazilian business tax ID), which I don't have as an individual.

## Security and privacy

- Screenshots have tenant IDs, object IDs, temporary passwords, personal emails, phone details, and the MFA QR code redacted. I keep the originals out of the repo.
- Every lab user has a strong password, and security defaults stay on. These accounts sit on a real public domain, so password-spray attempts are realistic.
- No Azure subscription is attached, so the tenant has no billable resources.

## Next

- GLPI ticketing instance with SLAs and categories, logging the scenarios from this lab as real tickets
- An AI help desk simulator where Claude plays the caller and grades how the ticket was handled

## Repo layout

```
it-help-desk-lab/
├── README.md
└── screenshots/   01 to 19, in walkthrough order
```
