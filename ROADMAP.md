# ALPHA LMS Roadmap

This roadmap describes intended work. Only repository documentation is in place; application features and AI experiments have not been implemented or tested.

## 1. Define the project

- [x] Prepare the academic project proposal.
- [x] Document the scope, course alignment, and conditional AI plan.
- [x] Establish a README, contribution guide, and Python ignore rules.
- [x] Agree on member responsibilities and acceptance criteria.

## 2. Build the core LMS

- [ ] Define stable IDs and account, course, assignment, quiz, and submission records.
- [ ] Create student, teacher, and administrator console workflows.
- [ ] Check role permissions and course enrollment.
- [ ] Organize course materials and local file references.
- [ ] Create assignments, deadlines, submission records, marks, and feedback.
- [ ] Implement teacher-approved multiple-choice quizzes and attempts.
- [ ] Preserve records in TXT/CSV/JSON and recover from invalid input or file failures.
- [ ] Add safe fictional demonstration data and verified setup instructions.

## 3. Add analysis and revision suggestions

- [ ] Clean and combine records using Pandas.
- [ ] Use NumPy for numerical summaries and vectorized calculations.
- [ ] Create line, bar, scatter, and histogram views with Matplotlib and Seaborn.
- [ ] Distinguish missing work from earned marks in progress summaries.
- [ ] Match missed quiz topics to relevant notes using transparent rules.
- [ ] Consider an optional public question-bank API for teacher-reviewed supplementary practice, with a local fallback.

## 4. Try later-course concepts as they are studied

Topics after Week 9 are yet to be studied in the proposal's learning plan. We will attempt suitable extensions after the corresponding lessons, subject to available time and data.

| Course session | Possible application |
| --- | --- |
| Week 10 / Lab 10 | Explore fitting a small notes classifier, train/test splitting, and evaluation. |
| Week 11 progress review | Reassess the core scope, progress, and extension feasibility. |
| Week 12 / Lab 11 | Compare a classifier with a keyword baseline and try cross-validation. |
| Week 13 / Lab 12 | Clean and normalize text; explore tokenization, Bag-of-Words, and TF-IDF for search and tagging. |
| Week 14 / Lab 13 | Optionally preprocess scanned notes with OpenCV; do not treat preprocessing as OCR or handwriting recognition. |
| Week 15 / Lab 14 | Improve documentation and modularity, review privacy and bias, and prepare the demonstration and viva. |

For any classifier, fit preprocessing on training data only and keep evaluation material separate. Report measured results and errors only after experiments are completed. Do not advertise a tentative extension as a finished feature.

## 5. Verify and demonstrate

- [ ] Test permissions, ownership, invalid inputs, missing files, and duplicate IDs.
- [ ] Test score bounds, incomplete attempts, and submission status changes.
- [ ] Check optional API failures and local recovery paths.
- [ ] Evaluate search/tagging if those features are developed.
- [ ] Review the repository for private student data and credentials.
- [ ] Document the actual features, limitations, dependencies, and run commands.
- [ ] Record each member's completed contributions.
