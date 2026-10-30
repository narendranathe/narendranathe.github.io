# HLD Cohort Mirror — Product Requirements

## Goal
Reproduce the authorized public-facing content, information architecture and responsive interactions of dhruvtechbytes.com as a separate GitHub Pages route. Payment, application processing, private cohort hub, and access-restricted simulators are out of scope.

## Jobs to be done
Visitors can understand the cohort, browse the week-by-week curriculum, review fourteen design exercises, inspect class examples, read feedback, and follow links to publicly available original simulators.

## Acceptance criteria
- Preserve core content sections and anchor navigation.
- Show nine curriculum weeks with expandable Saturday/Sunday material.
- Show fourteen design exercises, four free simulator entry points, sample class videos, creator information, testimonials, pricing information and FAQs.
- Functional responsive mobile navigation and native keyboard-accessible details/summary.
- No payment processing, fake authentication, tracking or collection of personal data.
- External original content links marked clearly; external simulators are linked rather than falsely claimed as locally replicated.
- No changes to existing root portfolio or /de-lab/ route.

## Known gaps / next iteration
This version mirrors public landing-page content and visual hierarchy, not the source's exact pixel geometry, complete word-for-word syllabus, testimonials or simulator code. External source images require source availability. Public simulators run on original site; restricted simulators, cohort hub, application forms and payment are not cloned. Perform screenshot regression comparisons before calling it a pixel-perfect replica.

## Delivery
GitHub Pages root workflow deploys /hld-cohort/ automatically from main. Review PR before merge. Validate public URL after deployment.
