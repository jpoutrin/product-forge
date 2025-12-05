---
name: Privacy Compliance
description: Automatic privacy and data protection guidance for GDPR (EU), CCPA (US), LGPD (Brazil), and other regulations
version: 1.0.0
triggers:
  - privacy
  - gdpr
  - ccpa
  - data protection
  - personal data
  - consent
  - cookies
  - data breach
  - dpo
  - lgpd
  - pipeda
  - user data
  - pii
---

# Privacy Compliance Skill

This skill automatically activates when working with personal data, privacy features, or compliance requirements. It provides region-specific guidance based on applicable regulations.

## Core Principle

**PRIVACY BY DESIGN, COMPLIANCE BY DEFAULT**

```
❌ Adding privacy as an afterthought
✅ Building privacy into every feature from the start
```

## Automatic Behaviors

When this skill activates, Claude will:

### 1. Identify Applicable Regulations

Based on context, identify which regulations apply:

```
JURISDICTION DETECTION
════════════════════════════════════════════════════════════

EU/EEA Users     → GDPR applies
UK Users         → UK GDPR applies
California Users → CCPA/CPRA applies
Brazil Users     → LGPD applies
Canada Users     → PIPEDA applies
Multiple Regions → Most restrictive applies

BUSINESS LOCATION
Company in EU    → GDPR applies globally for EU data
Company in US    → CCPA if meeting thresholds
```

### 2. Data Classification

Automatically prompt for data classification:

```
📊 DATA CLASSIFICATION
────────────────────────────────────────────────────────────

Personal Data (GDPR Article 4)
├── Direct identifiers (name, email, ID numbers)
├── Indirect identifiers (IP address, device IDs)
├── Location data
└── Online identifiers (cookies, user IDs)

Special Categories (GDPR Article 9) - HIGHER PROTECTION
├── Racial/ethnic origin
├── Political opinions
├── Religious/philosophical beliefs
├── Trade union membership
├── Genetic data
├── Biometric data (for identification)
├── Health data
└── Sex life/sexual orientation

Sensitive Personal Information (CCPA)
├── Government IDs
├── Financial account info
├── Precise geolocation
├── Contents of communications
└── Genetic data
```

### 3. Quick Compliance Checks

For any feature involving personal data:

```
✅ PRIVACY QUICK CHECK
────────────────────────────────────────────────────────────

□ What personal data is collected?
□ What is the legal basis for processing?
□ Is consent required? If so, is it:
  □ Freely given?
  □ Specific?
  □ Informed?
  □ Unambiguous?
□ How long will data be retained?
□ Who has access to the data?
□ Are there any international transfers?
□ How can users exercise their rights?
□ Is a DPIA required?
```

### 4. Region-Specific Requirements

#### GDPR (European Union)
```
GDPR ESSENTIALS
────────────────────────────────────────────────────────────

LEGAL BASES (pick one per processing activity)
├── Consent - User explicitly agrees
├── Contract - Necessary for service
├── Legal Obligation - Law requires it
├── Vital Interests - Protect someone's life
├── Public Task - Government function
└── Legitimate Interest - Balanced against rights

REQUIRED FOR COMPLIANCE
├── Privacy Notice - Clear, accessible
├── Consent Mechanism - No pre-ticked boxes
├── Cookie Banner - Granular choices
├── Rights Request Process - Respond in 30 days
├── Breach Notification - 72 hours to authority
├── Records of Processing - Document everything
└── DPO - Required in some cases

PENALTIES
└── Up to €20M or 4% global turnover
```

#### CCPA/CPRA (California)
```
CCPA/CPRA ESSENTIALS
────────────────────────────────────────────────────────────

APPLIES IF (any of)
├── Revenue > $25M
├── Buy/sell data of 100K+ consumers
└── 50%+ revenue from selling data

CONSUMER RIGHTS
├── Know - What data is collected
├── Delete - Request deletion
├── Opt-Out - "Do Not Sell My Info" link
├── Non-Discrimination - Equal service
├── Correct - Fix inaccurate data (CPRA)
└── Limit - Restrict sensitive data use (CPRA)

REQUIRED
├── Privacy Notice - At collection
├── Opt-Out Link - Homepage footer
├── Response Time - 45 days
└── Verification - Verify identity

PENALTIES
├── $2,500 per unintentional violation
└── $7,500 per intentional violation
```

#### France (CNIL Specific)
```
FRANCE/CNIL REQUIREMENTS
────────────────────────────────────────────────────────────

COOKIES (CNIL Guidelines)
├── No cookie wall (blocking access)
├── Easy reject as accept
├── Consent valid 6 months max
├── Keep proof of consent
└── French language required

ANALYTICS
├── Audience measurement can be exempt
├── Must be first-party only
├── Limited to aggregated stats
└── No cross-site tracking

DPO
├── Required for public authorities
├── Recommended for all
└── CNIL can be consulted
```

### 5. Implementation Patterns

#### Consent Collection
```typescript
// ✅ CORRECT: Granular, informed consent
interface ConsentRequest {
  purpose: string;           // Clear description
  dataCategories: string[];  // What data
  retention: string;         // How long
  recipients?: string[];     // Who receives
  international?: boolean;   // Cross-border?
}

async function requestConsent(request: ConsentRequest): Promise<boolean> {
  // Show clear, specific consent request
  // No pre-ticked boxes
  // Easy to refuse
  // Record consent with timestamp
}

// ❌ WRONG: Bundled, vague consent
function signup() {
  // "By signing up you agree to everything"
}
```

#### Data Subject Rights
```typescript
// ✅ CORRECT: Complete rights implementation
interface DataSubjectRequest {
  type: 'access' | 'deletion' | 'rectification' | 'portability' | 'objection';
  userId: string;
  verificationToken: string;
  submittedAt: Date;
}

async function handleDSR(request: DataSubjectRequest): Promise<void> {
  // 1. Verify identity
  // 2. Log request
  // 3. Process within deadline (30 days GDPR, 45 days CCPA)
  // 4. Respond to user
  // 5. Document completion
}
```

#### Data Minimization
```typescript
// ✅ CORRECT: Collect only what's needed
interface UserRegistration {
  email: string;      // Required for account
  password: string;   // Required for auth
  // No phone, DOB, address unless actually needed
}

// ❌ WRONG: Over-collection
interface UserRegistration {
  email: string;
  password: string;
  phone: string;        // Why?
  dateOfBirth: string;  // Why?
  address: string;      // Why?
  gender: string;       // Why?
}
```

### 6. Privacy-Safe Patterns

```typescript
// Pseudonymization
function pseudonymize(userId: string): string {
  return crypto.createHash('sha256').update(userId + SALT).digest('hex');
}

// Data retention
const RETENTION_POLICIES = {
  accountData: '3 years after account closure',
  sessionLogs: '90 days',
  analyticsRaw: '30 days',
  analyticsAggregated: '5 years',
  legalHold: '7 years',
};

// Right to be forgotten
async function deleteUserData(userId: string): Promise<void> {
  await Promise.all([
    deleteFromDatabase(userId),
    deleteFromBackups(userId),      // Schedule
    deleteFromAnalytics(userId),
    deleteFromThirdParties(userId), // Notify processors
    revokeConsents(userId),
  ]);
  await logDeletion(userId);
}

// Consent record
interface ConsentRecord {
  userId: string;
  purpose: string;
  givenAt: Date;
  method: 'checkbox' | 'banner' | 'form';
  ipAddress: string;
  userAgent: string;
  version: string;  // Privacy policy version
}
```

## Warning Triggers

Automatically warn user when:

1. **Collecting personal data without legal basis**
   > "⚠️ PRIVACY: Define legal basis for processing this personal data"

2. **Missing consent mechanism**
   > "⚠️ PRIVACY: Consent required for this processing - implement consent flow"

3. **Over-collecting data**
   > "⚠️ PRIVACY: Data minimization - only collect what's necessary for the purpose"

4. **No retention policy**
   > "⚠️ PRIVACY: Define retention period for this data"

5. **International transfer without safeguards**
   > "⚠️ PRIVACY: International transfer requires SCCs or other legal mechanism"

6. **Cookies without consent (EU)**
   > "⚠️ PRIVACY: Non-essential cookies require consent in EU"

7. **No privacy notice**
   > "⚠️ PRIVACY: Provide clear privacy notice before collecting data"

## Integration with Other Agents

- **DPO Expert**: Detailed compliance guidance
- **MCP Security Expert**: Technical security measures
- **Product Architect**: Privacy requirements in PRDs
- **CTO Architect**: Privacy by design in architecture

## Research Sources

When questions arise, research:
- **EU**: EDPB guidelines, CNIL guidance, national DPAs
- **US**: FTC guidance, California AG
- **Brazil**: ANPD guidance
- **General**: IAPP resources
