<script lang="ts">
import { goto } from '$app/navigation';
import { createCharacter } from '$lib/apis/character-chat';

let type: 'character' | 'story' = 'character';
let name = '';
let gender = '';
let age = '';
let details = '';
let prompt = '';
let imageUrl = '';

let isLoading = false;
let error = '';

let fileInput: HTMLInputElement;

async function handleImageUpload(e: Event) {
const target = e.target as HTMLInputElement;
if (target.files && target.files.length > 0) {
const file = target.files[0];
const formData = new FormData();
formData.append('file', file);

try {
const res = await fetch(`/api/v1/images/repository/upload`, {
method: 'POST',
headers: {
authorization: `Bearer ${localStorage.token}`
},
body: formData
});
if (res.ok) {
const data = await res.json();
imageUrl = data.url || `/api/v1/images/repository/${data.filename}`;
} else {
console.error("Image upload failed");
}
} catch (err) {
console.error("Image upload error", err);
}
}
}

async function saveCharacter() {
if (!name.trim()) {
error = '제목(이름)을 입력해주세요.';
return;
}

isLoading = true;
error = '';

try {
const newCharacter = {
type,
name,
gender: type === 'character' ? gender : '',
age: type === 'character' ? age : '',
details: type === 'character' ? details : '',
prompt: type === 'story' ? prompt : '',
imageUrl: imageUrl || 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'
};

const res = await createCharacter(localStorage.token, newCharacter);
if (res && res.id) {
goto('/character-chat');
} else {
error = '생성에 실패했습니다.';
}
} catch (err) {
error = err as string;
} finally {
isLoading = false;
}
}
</script>

<svelte:head>
<title>새로 만들기 | Open WebUI</title>
</svelte:head>

<div class="flex flex-col size-full items-center overflow-y-auto scrollbar relative px-4 py-8 bg-gray-50 dark:bg-gray-900">
<div class="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
<h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">새 항목 만들기</h1>

<div class="flex flex-col gap-5">

<div>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">분류</label>
<div class="flex gap-4">
<label class="flex items-center gap-2 cursor-pointer">
<input type="radio" bind:group={type} value="character" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
<span class="text-sm font-medium text-gray-900 dark:text-gray-300">캐릭터</span>
</label>
<label class="flex items-center gap-2 cursor-pointer">
<input type="radio" bind:group={type} value="story" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
<span class="text-sm font-medium text-gray-900 dark:text-gray-300">스토리</span>
</label>
</div>
</div>

<div>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{#if type === 'character'}캐릭터 이름{:else}스토리 제목{/if} *</label>
<input type="text" bind:value={name} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 text-gray-900 dark:text-gray-100" placeholder={type === 'character' ? '캐릭터의 이름을 입력하세요' : '스토리 제목을 입력하세요'}>
</div>

{#if type === 'character'}
<div class="grid grid-cols-2 gap-4">
<div>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">성별</label>
<input type="text" bind:value={gender} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 text-gray-900 dark:text-gray-100" placeholder="예: 여성, 남성">
</div>
<div>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">나이</label>
<input type="text" bind:value={age} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 text-gray-900 dark:text-gray-100" placeholder="예: 20세, 불명">
</div>
</div>

<div>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">세부 설정</label>
<p class="text-xs text-gray-500 mb-2">캐릭터의 성격, 말투, 과거사 등을 자유롭게 서술하세요.</p>
<textarea bind:value={details} rows="5" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 resize-y text-gray-900 dark:text-gray-100" placeholder="당신은 새침데기 츤데레 여동생입니다. 오빠를 귀찮아하면서도 속으로는 좋아합니다..."></textarea>
</div>
{:else}
<div>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">스토리 프롬프트</label>
<p class="text-xs text-gray-500 mb-2">스토리의 전반적인 배경, 세계관, AI의 역할을 통으로 작성하세요.</p>
<textarea bind:value={prompt} rows="8" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 resize-y text-gray-900 dark:text-gray-100" placeholder="당신은 판타지 세계의 던전 마스터입니다. 모험가(사용자)가 던전에 들어왔을 때 상황을 묘사하고 진행을 이끌어주세요..."></textarea>
</div>
{/if}

<div>
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">썸네일 이미지 URL</label>
<div class="flex gap-2">
<input type="text" bind:value={imageUrl} class="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 text-gray-900 dark:text-gray-100" placeholder="https://...">
<button type="button" class="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-lg font-medium transition-colors" on:click={() => fileInput.click()}>
파일 업로드
</button>
<input type="file" bind:this={fileInput} on:change={handleImageUpload} accept="image/*" class="hidden">
</div>
{#if imageUrl}
<div class="mt-3 relative w-32 h-48 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
<img src={imageUrl} alt="미리보기" class="object-cover w-full h-full">
</div>
{/if}
</div>

{#if error}
<div class="text-red-500 text-sm mt-2">{error}</div>
{/if}

<div class="flex justify-end gap-3 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
<button type="button" class="px-6 py-2.5 rounded-lg font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors" on:click={() => goto('/character-chat')}>취소</button>
<button type="button" class="px-6 py-2.5 rounded-lg font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 transition-colors" on:click={saveCharacter} disabled={isLoading || !name.trim()}>
{isLoading ? '생성 중...' : '만들기'}
</button>
</div>
</div>
</div>
</div>
