<script lang="ts">
import { goto } from '$app/navigation';

const characters = [
{
id: '1',
name: '들어오면 만지게 해줄게',
author: '맛도리네',
views: '350.3K',
rank: 1,
imageUrl: 'https://d394jeh9729epj.cloudfront.net/8uzw2bB3duM-GGKOOUpKVVo5/e790d9e0-d7ce-40d5-8b30-831078b97b1d_q70_gif600.webp'
},
{
id: '2',
name: '아카데미는 힘이 곧 매력',
author: '뮤지개',
views: '237.3K',
rank: 2,
imageUrl: 'https://d394jeh9729epj.cloudfront.net/8PT1uF8SRPy-GGKOTTVDQkdC/ee85cb99-c271-4d7d-87a8-1028c2041913_q70_gif600.webp'
},
{
id: '3',
name: '언제나 웃는 마을버스 R',
author: '대파조아',
views: '86.8K',
rank: 3,
imageUrl: 'https://d394jeh9729epj.cloudfront.net/8FnqcPT9U1q-GGKOWTBKWkgz/b7d7d118-cf88-44bf-bed0-2b40bb26bde9_w600.webp'
},
{
id: '4',
name: '혼수상태 여동생',
author: '땁따비땁',
views: '88.9K',
rank: 4,
imageUrl: 'https://d394jeh9729epj.cloudfront.net/8EissCzWvEQ-GGKOSVZXMzAw/3e466d8f-d21e-4fec-9583-e99995d5ee68_q70_gif600.webp'
},
{
id: '5',
name: '육상부 여신 타락일지',
author: '서단유',
views: '144.5K',
rank: 5,
imageUrl: 'https://d394jeh9729epj.cloudfront.net/8LJ9OImrLKo-GGKONDM1OUpP/333fe924-bf7a-4b0b-b827-39cee5dbe275_q70_gif600.webp'
},
{
id: '6',
name: '！우당탕탕！ 콘코르디아 아카데미 U',
author: '코기토',
views: '131.8K',
rank: 6,
imageUrl: 'https://d394jeh9729epj.cloudfront.net/8E7K2CU2heE-KKKOQ000M1I2/43fdc472-0402-4de6-8a9a-61220b9cd6a0_q70_gif600.webp'
}
];

function goToCharacter(id: string) {
goto(`/character-chat/${id}`);
}
</script>

<svelte:head>
<title>캐릭터 챗 | Open WebUI</title>
</svelte:head>

<div class="flex flex-col size-full items-center overflow-y-auto scrollbar relative px-4 py-8 bg-gray-50 dark:bg-gray-900">
<div class="w-full max-w-6xl">
<div class="flex flex-col gap-6 sm:gap-10">
<div class="flex w-full justify-center flex-col">
<div class="flex flex-col gap-3">
<div class="flex gap-2 items-center justify-between py-[11px]">
<div class="flex gap-3">
<button class="flex items-center gap-1 font-medium transition-colors h-6 rounded px-2 py-1 text-sm bg-transparent text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800">
성인 일간
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-4 h-4 fill-current"><path fill-rule="evenodd" d="m5.64 9.57 1.14-1.14L12 13.66l5.22-5.23 1.14 1.14L12 15.92z" clip-rule="evenodd"></path></svg>
</button>
<button class="flex items-center gap-1 font-medium transition-colors h-6 rounded px-2 py-1 text-sm bg-transparent text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800">
추천 인기순
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-4 h-4 fill-current"><path fill-rule="evenodd" d="m5.64 9.57 1.14-1.14L12 13.66l5.22-5.23 1.14 1.14L12 15.92z" clip-rule="evenodd"></path></svg>
</button>
</div>
</div>

<div class="grid w-full gap-y-5 gap-x-2 sm:gap-y-10 sm:gap-x-3 grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6">
{#each characters as character}
<div>
<div role="button" tabindex="0" class="w-full flex flex-col gap-3 text-left cursor-pointer transition-transform hover:scale-105" on:click={() => goToCharacter(character.id)} on:keydown={(e) => e.key === 'Enter' && goToCharacter(character.id)}>
<div class="relative rounded-lg overflow-hidden aspect-[2/3] bg-gray-200 dark:bg-gray-800">
<img alt={character.name} class="object-cover absolute inset-0 w-full h-full" src={character.imageUrl} />

<div class="w-full h-2/5 absolute bottom-0 bg-gradient-to-b from-transparent to-black/80"></div>

<div class="flex absolute bottom-0 w-full p-2.5 items-end gap-1">
<p class="text-3xl font-semibold text-white leading-none">{character.rank}</p>
</div>
</div>
<div class="flex flex-col gap-1 px-1">
<p class="text-base font-semibold text-gray-900 dark:text-gray-100 break-all line-clamp-2">{character.name}</p>
<div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
<span>{character.views}</span>
<div class="w-1 h-1 rounded-full bg-gray-400"></div>
<span class="truncate">{character.author}</span>
</div>
</div>
</div>
</div>
{/each}
</div>
</div>
</div>
</div>
</div>
</div>
