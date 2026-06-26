const fs = require('fs');

let content = fs.readFileSync('src/routes/character-chat/[id]/+page.svelte', 'utf-8');

// The prompt building currently assumes persona.name/gender/etc.
// We need to update it to support the new type field and use prompt for story.
// persona is initialized as let persona = { name: '', gender: '', age: '', details: '' };
// We need to add type: 'character' and prompt: '' to it.

content = content.replace(
    /let persona = \{\n\t\tname: '',\n\t\tgender: '',\n\t\tage: '',\n\t\tdetails: ''\n\t\};/,
    `let persona = {\n\t\ttype: 'character',\n\t\tname: '',\n\t\tgender: '',\n\t\tage: '',\n\t\tdetails: '',\n\t\tprompt: ''\n\t};`
);

const oldPromptLogic = `a.name || persona.details) {
finalSystemPrompt += \`\\n\\n[당신의 페르소나 설정]\\n\`;
if (persona.name) finalSystemPrompt += \`- 이름: \${persona.name}\\n\`;
if (persona.gender) finalSystemPrompt += \`- 성별: \${persona.gender}\\n\`;
if (persona.age) finalSystemPrompt += \`- 나이: \${persona.age}\\n\`;
if (persona.details) finalSystemPrompt += \`- 세부설정: \${persona.details}\\n\`;
}`;

const newPromptLogic = `a.type === 'story') {
if (persona.prompt) {
finalSystemPrompt += \`\\n\\n[스토리 설정]\\n\${persona.prompt}\\n\`;
}
} else {
if (persona.name || persona.details) {
finalSystemPrompt += \`\\n\\n[당신의 페르소나 설정]\\n\`;
if (persona.name) finalSystemPrompt += \`- 이름: \${persona.name}\\n\`;
if (persona.gender) finalSystemPrompt += \`- 성별: \${persona.gender}\\n\`;
if (persona.age) finalSystemPrompt += \`- 나이: \${persona.age}\\n\`;
if (persona.details) finalSystemPrompt += \`- 세부설정: \${persona.details}\\n\`;
}
}`;

content = content.replace(oldPromptLogic, newPromptLogic);

fs.writeFileSync('src/routes/character-chat/[id]/+page.svelte', content);
