detailed_summary = \
"""You are an AI assistant that is expert at summarizing text.

Give me detailed summary for below document, making sure all key points are covered.

Do not add any new information.
Do not miss any key points from the provided document

Document:
{{document}}
"""

atomic_facts = \
"""You are an AI assistant knowledgeable about {{domain}} domain. Be accurate but concise in response.

Please break down the following snippet from an article about {{domain}} into atomic facts.

1. Makesure each fact is grounded in the given text.
2. Include any necessary information needed to explain the fact or concept
3. The atomic facts should be as simple as possible, if it’s compound sentence, break down one more time
4. For clarity, avoid using pronouns like ’it’, ’he’, ’she’, ’this’, ’that’ etc., and instead use the full names or titles.
5. Focus only on key concepts and facts. Skip any question or problems mentioned in the passage.

To help you understand the task, here is an example:
[Passage]
The tournament was contested by ten national teams, maintaining the same format used in 2019. After six weeks of round-robin matches, India, South Africa, Australia, and New Zealand finished as the top four and qualified for the knockout stage. In the knockout stage, India and Australia beat New Zealand and South Africa, respectively, to advance to the final, played on 19 November at the Narendra Modi Stadium in Ahmedabad. Australia won the final by six wickets, winning their sixth Cricket World Cup title.
[Facts]
1. The tournament was contested by ten national teams.
2. The tournament maintained the same format used in 2019.
3. The round-robin matches lasted for six weeks.
4. India finished as one of the top four teams.
5. South Africa finished as one of the top four teams.
6. Australia finished as one of the top four teams.
7. New Zealand finished as one of the top four teams.
8. India, South Africa, Australia, and New Zealand qualified for the knockout stage.
9. In the knockout stage, India beat New Zealand.
10. In the knockout stage, Australia beat South Africa.
11. India advanced to the final.
12. Australia advanced to the final.
13. The final was played on 19 November.
14. The final was held at the Narendra Modi Stadium in Ahmedabad.
15. Australia won the final by six wickets.
16. Australia won their sixth Cricket World Cup title.
[End]

Now it's your turn breakdown following snippet from article about {{domain}} into atomic facts following similar style as above examples
[Passage]
{{document}}
[Facts]
"""

extractive_summary = \
"""You are an AI assistant that is expert at summarizing text.

Give me detailed extractive summary for below document, making sure all key points are covered.

Do not add any new information.
Do not miss any key points from the provided document


Document:
{{document}}
"""

generate_questions_and_responses = \
"""You are a very knowledgeable AI Assistant that will faithfully assist the user with their task.

Develop a series of educational question and answer pairs from a chapter in a {{domain}} textbook. 


The questions should:
* Be self-contained, not requiring references to tables, figures, or specific sections in the text for understanding.
* Focus on teaching and reinforcing the key knowledge and concepts presented in the chapter.
* Avoid sections with minimal educational content like index pages or prefaces. In such cases, respond with [UNANSWERABLE].
* Be directly relevant to the textbook's domain. For instance, in a science textbook, questions should revolve around scientific terms, definitions, and practical applications, while in a legal textbook, they should cover legal principles, case law, and precedents.
* Be formulated to allow for independent answers, avoiding direct references to specific theorems or text sections. For example, rather than asking 'Under what conditions is the fixed point of a function unique according to Theorem 3.1.5?', ask 'How does the Fixed Point Iteration method contribute to understanding function uniqueness?'
* Span a range of difficulty levels to accommodate a diverse student audience, from basic understanding to advanced comprehension.
* Include a variety of question types such as multiple-choice for basic recall, short answer for deeper understanding, and essay or problem-solving questions to test application and analysis skills.
* Align closely with the learning objectives of the textbook or the specific chapter, ensuring that the questions test the fundamental concepts and skills that the chapter aims to impart.

Strictly follow this format for each question answer pair your generate while responding

[QUESTION]
<Insert question here>
[ANSWER]
<Insert answer here>
[END]


Each question and answer pair should stand alone as a mini-lesson, encapsulating a key concept or idea from the chapter in a way that is accessible and informative without requiring the reader to refer back to the textbook.


Here are some examples of questions:

[Document]
{{icl_document}}

[QUESTION]
{{icl_query_1}}
[ANSWER]
{{icl_response_1}}
[END]

[QUESTION]
{{icl_query_2}}
[ANSWER]
{{icl_response_2}}
[END]

[QUESTION]
{{icl_query_3}}
[ANSWER]
{{icl_response_3}}
[END]


Here is the document:

[DOCUMENT]
{{document_outline}}
{{document}}
"""
