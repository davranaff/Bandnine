# Test Types in Exams

This file explains all supported question/task types in plain product language.

## 1) Reading

Reading is built from passages. Each passage contains blocks. Each block contains questions.

Reading block types:
- `true_false_ng`: user chooses `True`, `False`, or `Not Given`.
- `multiple_choice`: user picks one option.
- `list_of_options`: user picks one option from lettered list (dropdown style).
- `choose_title`: user picks the best title for a section.
- `matching_headings`: user matches a paragraph with one heading.
- `matching_paragraph_info`: user maps info to a paragraph.
- `matching_features`: user maps statements to people/places/groups.
- `matching_sentence_endings`: user chooses correct ending for sentence stem.
- `table_completion`: user fills blanks in a table using text answer.
- `note_completion`: user fills notes with text answer.
- `summary_completion`: user fills summary blanks with text answer.
- `sentence_completion`: user completes sentence blanks with text answer.
- `short_answers`: user writes short text answers.
- `flow_chart_completion`: user fills blanks in a flow chart.
- `diagram_completion`: user labels diagram blanks.

## 2) Listening

Listening is built from parts. All parts in one test share one common audio (`voice_url`).

Listening block types:
- `multiple_choice`: user picks one option.
- `list_of_options`: user picks from provided option list.
- `matching`: user matches statements with options.
- `map_plan_labelling`: user labels a map/plan by choosing options.
- `table_completion`: user fills table blanks with text.
- `note_completion`: user fills notes with text.
- `form_completion`: user fills form fields with text.
- `sentence_completion`: user completes sentence blanks with text.
- `summary_completion`: user fills summary blanks with text.
- `short_answer`: user writes short text answer.
- `short_answer_multiple`: same as short answer for multiple items.
- `diagram_flowchart_completion`: user fills diagram/flowchart text blanks.

## 3) Writing

Writing test has parts (usually Task 1 and Task 2).

Per writing part:
- prompt text is provided;
- optional image can be provided;
- optional files can be attached;
- answer is always essay text input.

No separate options/matching in writing.

## 4) How frontend should treat answer mode

For reading/listening blocks, backend returns `answer_spec`:
- `answer_type=single_choice`: show radio or dropdown depending on `input_variant`.
- `answer_type=text_input`: show text blanks/table blanks depending on `input_variant`.

For writing parts:
- `answer_type=text_input` and `input_variant=essay`: show essay textarea.
