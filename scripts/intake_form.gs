/**
 * Builds the Morganton Scientific article submission form (the "intake form") in Google Forms.
 *
 * HOW TO RUN IT
 *   1. Go to https://script.google.com, signed in as the account that will own the form, and
 *      click New project.
 *   2. Delete the code in the editor, paste in this whole file, and save.
 *   3. Optional: put a Drive folder's ID in FOLDER_ID below (the part of the folder's URL after
 *      /folders/). Leave it empty to put the form and its Sheet in My Drive. Don't use a Shared
 *      Drive: Google won't let a form there keep file-upload questions.
 *   4. Choose buildIntakeForm in the function menu and click Run. Google asks you to approve
 *      access to your Forms, Sheets and Drive the first time.
 *   5. Open View → Logs (or Execution log) for the form's links and the steps that remain.
 *
 * Each run makes a new form; it never changes an existing one.
 *
 * WHAT IT CAN'T DO
 *   Google's scripting service can't create file-upload questions. The script leaves a marked
 *   placeholder in Section 9, and the log lists the five upload questions to add by hand.
 *
 * The questions follow the "Author intake form" tab of the Volume 4 meeting doc. If you change
 * one, change it here too.
 */

const TITLE = 'Morganton Scientific, Volume 4: article submission';
const FOLDER_ID = '';           // Drive folder for the form and its Sheet; empty means My Drive
const AUTHOR_SECTIONS = 6;      // one section per author

const DESCRIPTION = [
  'Fill this in once per article, when your manuscript is final. If your article has ' +
    'co-authors, the corresponding author (the person readers can contact) fills it in for ' +
    'everyone. It takes about ten minutes.',
  'Have these ready: the ORCID for every author (register free at orcid.org/register, it takes ' +
    'two minutes), each author\'s contribution, your final manuscript, every figure as a ' +
    'separate file, and your bibliography exported from Zotero or another reference manager.',
  'Names, ORCIDs, contributions and keywords are published with your article and become part of ' +
    'its permanent DOI record, so check them carefully. The Author\'s Guide explains every ' +
    'question: https://github.com/ncssm/morgantonscientific2027/blob/main/docs/author-guide.md',
].join('\n\n');

const SUBJECTS = ['Biology', 'Chemistry', 'Physics', 'Engineering', 'Public Health',
  'Computer Science', 'Other'];

const CREDIT_ROLES = [
  'Conceptualization: the ideas, the research question',
  'Data curation: managing and organizing the data',
  'Formal analysis: statistics, modeling, the math',
  'Funding acquisition: securing grants or materials',
  'Investigation: running the experiments',
  'Methodology: designing how it would be done',
  'Project administration: coordinating and scheduling',
  'Resources: supplying materials, samples, equipment',
  'Software: code you wrote',
  'Supervision: overseeing others\' work',
  'Validation: verifying that the results hold up',
  'Visualization: making the figures',
  'Writing – original draft: writing the first version',
  'Writing – review & editing: revising, responding to feedback',
];

const FINAL_CHECKS = [
  'Every figure and table is mentioned in my text',
  'Figures and tables are numbered in the order they\'re first mentioned',
  'Everything I cite is in my bibliography, and everything in it is cited',
  'I\'ve proofread the title, and every co-author has seen these answers',
];

const UPLOAD_QUESTIONS = [
  '9.1 Manuscript (required). Help: "The final version, as a Word file, Google Doc or PDF." ' +
    'Settings: allow only Document and PDF, 1 file, 10 MB.',
  '9.2 Figures (not required). Help: "Each figure as a separate file at the largest size you ' +
    'have: 300 dpi, or at least 2000 pixels on the long edge. Name them by number, e.g. ' +
    'figure1.png. More than 10? Upload a .zip." Settings: no type restriction, 10 files, 100 MB.',
  '9.3 Tables (not required). Help: "Only if a table isn\'t already typed out in your ' +
    'manuscript: upload it as a spreadsheet. Never a screenshot of a table." Settings: allow ' +
    'only Spreadsheet, 5 files, 10 MB.',
  '9.4 Bibliography (required). Help: "Export a .bib file from Zotero, Mendeley or EndNote. ' +
    'Every source you cite must be in it, and everything in it must be cited." Settings: no ' +
    'type restriction (Google has no category for .bib), 1 file, 10 MB.',
  '9.5 Code and data (not required). Help: "Code you wrote or data you collected, if you want ' +
    'it published alongside the article. Several files? Upload a .zip. If it already lives in a ' +
    'public repository, put the link in 12.2 instead." Settings: no type restriction, 5 files, ' +
    '100 MB.',
];

function buildIntakeForm() {
  const form = FormApp.create(TITLE);
  form.setDescription(DESCRIPTION);
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);
  form.setLimitOneResponsePerUser(false);   // an author with two articles submits twice
  form.setConfirmationMessage('Thanks, your submission is in. An editor will be in touch about ' +
    'anything that\'s missing.');

  const notes = [];
  try {
    form.setEmailCollectionType(FormApp.EmailCollectionType.VERIFIED);
  } catch (e) {
    form.setCollectEmail(true);
    notes.push('Check Settings → Responses → Collect email addresses is set to Verified.');
  }
  try {
    form.setRequireLogin(true);   // NCSSM accounts only; works only for Workspace owners
  } catch (e) {
    notes.push('Couldn\'t restrict the form to NCSSM accounts. That setting only exists when ' +
      'the form is owned by an NCSSM Google account.');
  }

  // Section 2: the article. (Section 1 is the title and description above.)
  form.addPageBreakItem().setTitle('The article');
  form.addTextItem().setTitle('Article title').setRequired(true)
    .setHelpText('Exactly as it should be published. It goes into the permanent DOI record, so ' +
      'proofread it letter by letter. No period at the end.');
  form.addMultipleChoiceItem().setTitle('What kind of article is this?').setRequired(true)
    .setChoiceValues(['Research paper', 'Essay']);
  form.addListItem().setTitle('Subject').setRequired(true).setChoiceValues(SUBJECTS);
  form.addParagraphTextItem().setTitle('Keywords').setRequired(true)
    .setHelpText('Up to five, one per line. Choose terms someone would search for; prefer the ' +
      'specific ("negative geotaxis") to the general ("biology"). Don\'t repeat words from your ' +
      'title.')
    .setValidation(FormApp.createParagraphTextValidation()
      .setHelpText('Five keywords at most, one per line.')
      .requireTextMatchesPattern('^[^\\n]+(\\n[^\\n]+){0,4}$')
      .build());
  form.addTextItem().setTitle('Short title')
    .setHelpText('A shorter version of the title for the page header in print, if the full ' +
      'title is long.');
  form.addTextItem().setTitle('Corresponding author').setRequired(true)
    .setHelpText('The one author readers can contact after publication, usually you. Their ' +
      'name exactly as you\'ll enter it in the author sections.');

  // Sections 3 to 8: one per author. Each but the last ends with "Is there another author?",
  // whose answers jump to the next author or to Files; those choices are set once both exist.
  const authorPages = [];
  const anotherQuestions = [];
  for (let n = 1; n <= AUTHOR_SECTIONS; n++) {
    authorPages.push(form.addPageBreakItem().setTitle('Author ' + n).setHelpText(n === 1
      ? 'Start with yourself. Then add your co-authors in the order they should appear in print.'
      : 'The next author, in print order.'));
    addAuthorQuestions(form);
    if (n < AUTHOR_SECTIONS) {
      anotherQuestions.push(form.addMultipleChoiceItem().setTitle('Is there another author?')
        .setRequired(true));
    }
  }

  // Section 9: files. The upload questions are added by hand; see the log.
  const filesPage = form.addPageBreakItem().setTitle('Files').setHelpText('Upload the final ' +
    'versions. Every figure as its own file, at full resolution, not only pasted into your ' +
    'document.');
  form.addSectionHeaderItem().setTitle('EDITORS: add the five file-upload questions here, then ' +
    'delete this note. The steps are in the script\'s log.');

  anotherQuestions.forEach((q, i) => q.setChoices([
    q.createChoice('Yes', authorPages[i + 1]),
    q.createChoice('No', filesPage),
  ]));

  // Sections 10 to 12: figures from elsewhere, then the final checks.
  form.addPageBreakItem().setTitle('Figures');
  const ownFigures = form.addMultipleChoiceItem()
    .setTitle('Did you and your co-authors make every figure in this article?').setRequired(true);
  const elsewherePage = form.addPageBreakItem().setTitle('Figures from elsewhere');
  form.addParagraphTextItem().setTitle('Which figures, and where did each come from?')
    .setRequired(true)
    .setHelpText('One per line, e.g. "Figure 2: adapted from Smith et al. 2021, Figure 3". ' +
      'Citing a source is not the same as having permission to republish it. We publish under ' +
      'CC-BY, which lets anyone reuse what we publish, and we can only grant that for material ' +
      'we own. An editor will talk through the options with you.');
  const checksPage = form.addPageBreakItem().setTitle('Before you submit');
  ownFigures.setChoices([
    ownFigures.createChoice('Yes, every figure is our own', checksPage),
    ownFigures.createChoice('No, at least one comes from somewhere else', elsewherePage),
  ]);
  form.addCheckboxItem().setTitle('Final checks').setRequired(true)
    .setChoiceValues(FINAL_CHECKS)
    .setValidation(FormApp.createCheckboxValidation()
      .setHelpText('Please check all four before submitting.')
      .requireSelectExactly(FINAL_CHECKS.length)
      .build());
  form.addParagraphTextItem().setTitle('Anything else we should know?')
    .setHelpText('Anything the editors should know, e.g. a co-author who left NCSSM, or a figure ' +
      'you\'re still redrawing.');

  // The response Sheet, and both files into the chosen folder.
  const sheet = SpreadsheetApp.create(TITLE + ' (Responses)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());
  if (FOLDER_ID) {
    const folder = DriveApp.getFolderById(FOLDER_ID);
    DriveApp.getFileById(form.getId()).moveTo(folder);
    DriveApp.getFileById(sheet.getId()).moveTo(folder);
  }

  Logger.log([
    'Form built.',
    'Edit it:     ' + form.getEditUrl(),
    'Respondents: ' + form.getPublishedUrl(),
    'Responses:   ' + sheet.getUrl(),
    '',
    'Still to do in the form editor:',
    '1. In the Files section, delete the "EDITORS: add the five file-upload questions" note and ' +
      'add these, each with Add question → File upload:',
  ].concat(UPLOAD_QUESTIONS.map(q => '   - ' + q), [
    '2. Test the keyword rule with six lines, and the ORCID rule with a bad value: neither ' +
      'pattern has been tried in Google Forms yet.',
    '3. Share the response Sheet and, once the first upload arrives, its "(File responses)" ' +
      'folder with the editors.',
  ], notes.map((n, i) => (i + 4) + '. ' + n)).join('\n'));
}

function addAuthorQuestions(form) {
  form.addTextItem().setTitle('Full name').setRequired(true)
    .setHelpText('Exactly as it should be printed, and the same form everywhere: in the ' +
      'article, in emails, on your ORCID record. "Jordan M. Smith" and "Jordan Smith" are ' +
      'different people to an indexing system.');
  form.addTextItem().setTitle('ORCID').setRequired(true)
    .setHelpText('Every author needs their own. Register free at orcid.org/register. Full form, ' +
      'e.g. 0000-0002-1825-0097.')
    .setValidation(FormApp.createTextValidation()
      .setHelpText('Use the full form with dashes, e.g. 0000-0002-1825-0097.')
      .requireTextMatchesPattern('^\\d{4}-\\d{4}-\\d{4}-\\d{3}[\\dX]$')
      .build());
  form.addTextItem().setTitle('Email').setRequired(true)
    .setHelpText('One that will still work after graduation. It goes into the article\'s ' +
      'metadata.')
    .setValidation(FormApp.createTextValidation().requireTextIsEmail().build());
  form.addMultipleChoiceItem().setTitle('School').setRequired(true)
    .setChoiceValues(['NCSSM']).showOtherOption(true);
  form.addCheckboxItem().setTitle('Contribution').setRequired(true)
    .setHelpText('Check every role this author had.')
    .setChoiceValues(CREDIT_ROLES);
}
