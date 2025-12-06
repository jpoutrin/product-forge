# RFC Evaluation Matrix

This reference provides standard evaluation criteria and rating systems for objective RFC analysis.

## Standard Criteria Categories

### Technical Criteria

| Criterion | Description | How to Measure |
|-----------|-------------|----------------|
| **Performance** | System response time, throughput, resource efficiency | Benchmarks, load tests, profiling |
| **Scalability** | Ability to handle growth in users, data, or requests | Theoretical analysis, scaling tests |
| **Reliability** | Uptime, fault tolerance, error handling | SLA targets, failure mode analysis |
| **Security** | Protection against threats, data safety, compliance | Security audit, threat modeling |
| **Maintainability** | Ease of understanding, modifying, debugging | Code complexity metrics, review |
| **Testability** | Ease of writing and running tests | Coverage potential, test isolation |
| **Observability** | Ability to monitor, debug, and understand behavior | Logging, metrics, tracing support |

### Operational Criteria

| Criterion | Description | How to Measure |
|-----------|-------------|----------------|
| **Deployment Complexity** | Ease of deploying and rolling back | CI/CD integration, deployment steps |
| **Operational Overhead** | Ongoing maintenance and support needs | On-call burden, manual interventions |
| **Monitoring Support** | Built-in monitoring and alerting | Metrics endpoints, log quality |
| **Documentation** | Quality and completeness of docs | Documentation audit |
| **Learning Curve** | Time for team to become proficient | Training needs assessment |

### Business Criteria

| Criterion | Description | How to Measure |
|-----------|-------------|----------------|
| **Implementation Cost** | Development effort and resources | Story points, person-days |
| **Operational Cost** | Infrastructure and maintenance costs | Cost modeling |
| **Time to Value** | Speed to first usable version | Project timeline |
| **Risk Level** | Technical and business risk | Risk assessment matrix |
| **Flexibility** | Ability to adapt to changing requirements | Architecture review |
| **Team Expertise** | Team's familiarity with required technologies | Skills assessment |

## Rating Scales

### Qualitative Scale (5-point)

| Rating | Label | Description |
|--------|-------|-------------|
| 5 | Excellent | Exceeds requirements significantly |
| 4 | Good | Meets all requirements well |
| 3 | Adequate | Meets minimum requirements |
| 2 | Poor | Partially meets requirements |
| 1 | Inadequate | Does not meet requirements |

### Risk/Impact Scale

| Rating | Label | Description |
|--------|-------|-------------|
| High | Critical | Major impact, requires immediate attention |
| Medium | Significant | Notable impact, needs consideration |
| Low | Minor | Minimal impact, acceptable |

### Effort Scale

| Rating | Description |
|--------|-------------|
| XS | < 1 day |
| S | 1-3 days |
| M | 1-2 weeks |
| L | 2-4 weeks |
| XL | 1-3 months |
| XXL | > 3 months |

## Weighted Scoring Template

### Assigning Weights

Weights should sum to 100% and reflect the priorities for this specific decision:

```markdown
| Criterion | Weight | Justification |
|-----------|--------|---------------|
| Performance | 25% | Critical for user experience |
| Security | 20% | Handles sensitive data |
| Implementation Cost | 20% | Limited budget |
| Maintainability | 15% | Long-term system |
| Scalability | 10% | Expected growth |
| Learning Curve | 10% | New team members joining |
| **Total** | **100%** | |
```

### Calculating Weighted Scores

```markdown
| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Performance | 25% | 4 (1.00) | 5 (1.25) | 3 (0.75) |
| Security | 20% | 5 (1.00) | 4 (0.80) | 5 (1.00) |
| Cost | 20% | 3 (0.60) | 2 (0.40) | 4 (0.80) |
| Maintainability | 15% | 4 (0.60) | 3 (0.45) | 4 (0.60) |
| Scalability | 10% | 3 (0.30) | 5 (0.50) | 3 (0.30) |
| Learning | 10% | 4 (0.40) | 2 (0.20) | 5 (0.50) |
| **Weighted Total** | | **3.90** | **3.60** | **3.95** |
```

## Objectivity Checklist

Before finalizing options analysis:

- [ ] Each option has at least 3 advantages documented
- [ ] Each option has at least 3 disadvantages documented
- [ ] All claims are supported by evidence or clearly marked as assumptions
- [ ] No superlatives ("best", "obvious", "clearly superior")
- [ ] Evaluation criteria were defined BEFORE scoring options
- [ ] The same criteria are applied consistently to all options
- [ ] Scoring justifications are provided, not just numbers
- [ ] Trade-offs are explicitly acknowledged for the recommendation
- [ ] Dissenting viewpoints are documented fairly

## Common Evaluation Mistakes

### Avoid These Patterns

1. **Confirmation Bias**
   - Problem: Favoring an option you already prefer
   - Fix: Define criteria before analyzing options

2. **Scope Creep in Criteria**
   - Problem: Adding criteria to favor a specific option
   - Fix: Lock criteria before scoring

3. **False Precision**
   - Problem: Using detailed scores without supporting data
   - Fix: Use ranges or qualitative ratings when data is limited

4. **Missing Options**
   - Problem: Not considering all viable alternatives
   - Fix: Brainstorm options before evaluating

5. **Status Quo Bias**
   - Problem: Unfairly favoring "do nothing" or existing solution
   - Fix: Evaluate current state with same rigor as new options

6. **Dismissive Analysis**
   - Problem: Superficially rejecting options ("not worth considering")
   - Fix: Document specific reasons for any option not fully analyzed

## Context-Specific Criteria

### For API Design Decisions

- API ergonomics and developer experience
- Backward compatibility requirements
- Documentation generation support
- SDK generation feasibility
- Rate limiting and quota management

### For Database Selection

- Query patterns and optimization
- Data consistency requirements
- Backup and recovery capabilities
- Replication and high availability
- Migration complexity from current system

### For Framework/Library Selection

- Community size and activity
- Long-term maintenance likelihood
- License compatibility
- Integration with existing stack
- Upgrade path complexity

### For Architecture Patterns

- Team expertise and learning curve
- Operational complexity
- Debugging and troubleshooting difficulty
- Testing strategy complexity
- Deployment and rollback processes
