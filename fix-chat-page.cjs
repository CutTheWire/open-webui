const fs = require('fs');

let content = fs.readFileSync('src/routes/character-chat/[id]/+page.svelte', 'utf-8');

// Replace PREDEFINED_CHARACTERS entirely and add the import
content = content.replace(
    /const PREDEFINED_CHARACTERS: Record[\s\S]*?'10대', details: '활발하고 시끄러운 성격. 장난기 많은 말투.'\n\t\t\}\n\t};\n/m,
    `import { getCharacterById } from '$lib/apis/character-chat';\n\n`
);

// Update onMount
content = content.replace(
    /const id = \$page\.params\.id;\n\t\tif \(id && PREDEFINED_CHARACTERS\[id\]\) \{\n\t\t\tpersona = PREDEFINED_CHARACTERS\[id\];\n\t\t\}/,
    `const id = $page.params.id;
if (id) {
getCharacterById(localStorage.token, id).then(data => {
if (data) {
persona = data;
}
}).catch(err => console.error("Failed to load character", err));
}`
);

fs.writeFileSync('src/routes/character-chat/[id]/+page.svelte', content);
