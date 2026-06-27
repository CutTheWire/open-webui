const fs = require('fs');

let content = fs.readFileSync('src/routes/character-chat/create/+page.svelte', 'utf-8');

// In Svelte, curly braces inside text are fine, but maybe there's a parsing issue with the ternary.
// Let's replace `{type === 'character' ? '캐릭터 이름' : '스토리 제목'}` with an {#if} block.

const oldStr = "{type === 'character' ? '캐릭터 이름' : '스토리 제목'}";
const newStr = "{#if type === 'character'}캐릭터 이름{:else}스토리 제목{/if}";

content = content.replace(oldStr, newStr);

fs.writeFileSync('src/routes/character-chat/create/+page.svelte', content);
