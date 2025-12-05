# Product Increments Process

**Iterative Product Development in 4-6 Week Cycles**

---

## 🎯 When to Use Product Increments

Use this approach when:
- Building products iteratively with continuous feedback
- Working in agile/scrum environments
- Need to validate assumptions before full build
- Want to reduce risk through smaller releases
- Prefer learning-driven development

**Prerequisites**: Complete Product Positioning first (`claude_settings/python/processes/product-positioning.md`)

---

## 📁 Increment-Based File Structure

```
product-docs/
├── 00-foundation/                        # One-time foundational work
│   ├── positioning/                      # From product-positioning.md
│   │   ├── positioning-statement.md
│   │   ├── brand-personality.md
│   │   └── vision-alignment.md
│   ├── discovery/                        # Initial 20-question discovery
│   │   ├── discovery-session.md
│   │   ├── market-research.md
│   │   └── competitive-landscape.md
│   └── core-strategy/
│       ├── product-vision.md
│       ├── mission-statement.md
│       └── business-model.md
│
├── increments/                           # Iterative development cycles
│   ├── increment-001-mvp/
│   │   ├── planning/
│   │   │   ├── increment-brief.md       # Goals, scope, success criteria
│   │   │   ├── feature-selection.md     # Which features for this increment
│   │   │   └── timeline.md
│   │   ├── user-research/
│   │   │   ├── personas-v1.md           # Personas for this increment
│   │   │   ├── user-interviews/
│   │   │   └── journey-maps/
│   │   ├── features/
│   │   │   ├── prds/                    # PRDs for increment features
│   │   │   ├── user-stories/
│   │   │   └── wireframes/
│   │   ├── development/
│   │   │   ├── technical-specs/
│   │   │   ├── sprint-plans/
│   │   │   └── task-list.md             # Generated from PRDs
│   │   ├── launch/
│   │   │   ├── go-to-market.md
│   │   │   └── success-metrics.md
│   │   └── retrospective/
│   │       ├── metrics-review.md
│   │       ├── user-feedback.md
│   │       └── lessons-learned.md
│   │
│   └── increment-002-growth/             # Next increment
│       └── [same structure]
│
├── living-docs/                          # Continuously updated
│   ├── roadmap/
│   │   ├── current-roadmap.md
│   │   └── backlog.md
│   ├── metrics/
│   │   └── dashboard.md
│   └── architecture/
│       └── system-design.md
│
└── templates/                            # Reusable templates
    ├── increment-brief-template.md
    ├── prd-template.md
    └── retrospective-template.md
```

---

## 🔄 Increment Workflow (4-6 weeks)

### Phase 1: Foundation (Once Only)
**Time**: 1-2 weeks initially

1. **Product Positioning** (Required first)
   - Run positioning discovery session
   - Define brand and vision
   - Create positioning statement

2. **Core Discovery**
   - Initial 20-question product discovery
   - Market research and competitive analysis
   - Core strategy and business model

3. **Living Documents Setup**
   - Initialize roadmap
   - Set up metrics dashboard
   - Create architecture baseline

### Phase 2: Increment Planning (1-2 days)
**For each increment:**

1. **Review Previous Increment**
   - Analyze retrospective findings
   - Review metrics and user feedback
   - Identify carry-over items

2. **Define Increment Scope**
   - Select 3-5 features from backlog
   - Set specific increment goals
   - Define success criteria

3. **Create Increment Brief**
   ```markdown
   # Increment Brief: increment-XXX-{theme}
   
   ## Goals
   - Primary: [Main objective]
   - Secondary: [Supporting objectives]
   
   ## Features
   1. [Feature 1] - [Why now?]
   2. [Feature 2] - [Why now?]
   
   ## Success Criteria
   - [ ] [Measurable outcome 1]
   - [ ] [Measurable outcome 2]
   
   ## Timeline
   - Week 1: Discovery & Design
   - Week 2-3: Development
   - Week 4: Launch & Learn
   ```

### Phase 3: Mini Discovery (2-3 days)

1. **Targeted User Research**
   - Interview 3-5 users about increment features
   - Update personas if needed
   - Map specific user journeys

2. **Technical Discovery**
   - Assess technical requirements
   - Identify dependencies
   - Plan architecture changes

3. **Design Discovery**
   - Wireframe new features
   - Update design system if needed
   - Create prototypes for testing

### Phase 4: Feature Development (2-4 weeks)

1. **PRD Creation**
   - Write PRDs for increment features only
   - Focus on MVP scope
   - Include clear acceptance criteria

2. **Task Generation**
   - Use task-generation.md process
   - Create granular task list
   - Map tasks to sprint plan

3. **Iterative Build**
   - Daily standups
   - Weekly demos
   - Continuous integration

### Phase 5: Launch & Learn (1 week)

1. **Increment Release**
   - Deploy to staging/production
   - Run launch checklist
   - Monitor initial metrics

2. **Gather Feedback**
   - User interviews
   - Analytics review
   - Support ticket analysis

3. **Measure Success**
   - Compare to success criteria
   - Document key metrics
   - Identify surprises

### Phase 6: Retrospective (1 day)

1. **Team Retrospective**
   - What went well?
   - What could improve?
   - What did we learn?

2. **Product Learning**
   - User behavior insights
   - Feature performance
   - Market response

3. **Next Increment Input**
   - Prioritize backlog items
   - Identify new opportunities
   - Plan improvements

---

## 📊 Increment Examples

### increment-001-mvp
**Theme**: Core Value Proposition
- User authentication
- Basic workflow
- Essential features only
- Focus: Prove product-market fit

### increment-002-growth
**Theme**: User Acquisition
- Onboarding improvements
- Viral features
- Referral system
- Focus: Reduce friction, increase sharing

### increment-003-scale
**Theme**: Performance & Reliability
- Infrastructure improvements
- Performance optimization
- Error handling
- Focus: Handle 10x users

### increment-004-mobile
**Theme**: Mobile Experience
- Responsive design
- Mobile app
- Offline capabilities
- Focus: Reach mobile users

### increment-005-enterprise
**Theme**: B2B Features
- Team management
- Advanced permissions
- Enterprise SSO
- Focus: Capture enterprise market

---

## 🎯 Key Principles

### 1. Foundation First
- Always complete positioning before increments
- Foundation is done once, not repeated
- Living docs evolve with each increment

### 2. Time-Boxed Cycles
- Strict 4-6 week increments
- Ship something every cycle
- Learn and adjust quickly

### 3. Continuous Learning
- Each increment informs the next
- Retrospectives are mandatory
- Pivot based on data, not opinions

### 4. Documentation Balance
- Document enough to remember why
- Don't over-document
- Keep living docs current

### 5. User-Centered Iterations
- Talk to users every increment
- Ship to learn, not to perfect
- Features earn their way to the next increment

---

## 📋 Templates

### Increment Brief Template
See: `templates/increment-brief-template.md`

### Retrospective Template
See: `templates/retrospective-template.md`

### Sprint Plan Template
See: `templates/sprint-plan-template.md`

---

## 🚀 Getting Started

1. **First Time?**
   - Complete Product Positioning first
   - Run full Product Discovery (20 questions)
   - Set up living documents
   - Plan your first increment (MVP)

2. **Continuing?**
   - Review last retrospective
   - Check metrics dashboard
   - Plan next increment
   - Start with mini discovery

3. **Integration with Other Processes**
   - Use `task-generation.md` for PRD → tasks
   - Use `task-management.md` for execution
   - Reference main `product-development.md` for detailed phases

---

## ⚠️ Common Pitfalls to Avoid

1. **Skipping Foundation** - Always do positioning first
2. **Increment Creep** - Stick to 4-6 week cycles
3. **Feature Overload** - Limit to 3-5 features per increment
4. **Ignoring Retrospectives** - Learning is the whole point
5. **Perfect vs. Good** - Ship to learn, iterate to improve

---

*Product increments let you build better products faster by shipping small, learning quickly, and iterating based on real user feedback.*