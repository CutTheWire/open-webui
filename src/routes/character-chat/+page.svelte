<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getCharacters } from '$lib/apis/character-chat';

	let characters: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			const res = await getCharacters(localStorage.token);
			if (res) {
				characters = res;
			}
		} catch (error) {
			console.error('Failed to load characters:', error);
		} finally {
			loading = false;
		}
	});

	function goToCharacter(id: string) {
		goto(`/character-chat/${id}`);
	}

	function goToCreate() {
		goto(`/character-chat/create`);
	}
</script>

<svelte:head>
	<title>캐릭터 챗 | Open WebUI</title>
</svelte:head>

<div
	class="flex flex-col size-full items-center overflow-y-auto scrollbar relative px-4 py-8 bg-gray-50 dark:bg-gray-900"
>
	<div class="w-full max-w-6xl">
		<div class="flex flex-col gap-6 sm:gap-10">
			<div class="flex w-full justify-center flex-col">
				<div class="flex flex-col gap-3">
					<div class="flex gap-2 items-center justify-between py-[11px]">
						<div class="flex gap-3">
							<button
								class="flex items-center gap-1 font-medium transition-colors h-6 rounded px-2 py-1 text-sm bg-transparent text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800"
							>
								성인 일간
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									class="w-4 h-4 fill-current"
									><path
										fill-rule="evenodd"
										d="m5.64 9.57 1.14-1.14L12 13.66l5.22-5.23 1.14 1.14L12 15.92z"
										clip-rule="evenodd"
									></path></svg
								>
							</button>
							<button
								class="flex items-center gap-1 font-medium transition-colors h-6 rounded px-2 py-1 text-sm bg-transparent text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800"
							>
								추천 인기순
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									class="w-4 h-4 fill-current"
									><path
										fill-rule="evenodd"
										d="m5.64 9.57 1.14-1.14L12 13.66l5.22-5.23 1.14 1.14L12 15.92z"
										clip-rule="evenodd"
									></path></svg
								>
							</button>
						</div>

						<!-- Create Character Button -->
						<button
							on:click={goToCreate}
							class="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2 transition-colors text-sm"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke-width="2"
								stroke="currentColor"
								class="w-4 h-4"
							>
								<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
							</svg>
							새 캐릭터 만들기
						</button>
					</div>

					{#if loading}
						<div class="flex justify-center items-center py-20">
							<div
								class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"
							></div>
						</div>
					{:else if characters.length === 0}
						<div
							class="flex flex-col items-center justify-center py-20 text-gray-500 dark:text-gray-400"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								class="w-12 h-12 mb-4"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
							<p>생성된 캐릭터가 없습니다. 첫 캐릭터를 만들어보세요!</p>
						</div>
					{:else}
						<div
							class="grid w-full gap-y-5 gap-x-2 sm:gap-y-10 sm:gap-x-3 grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6"
						>
							{#each characters as character}
								<div>
									<div
										role="button"
										tabindex="0"
										class="w-full flex flex-col gap-3 text-left cursor-pointer transition-transform hover:scale-105"
										on:click={() => goToCharacter(character.id)}
										on:keydown={(e) => e.key === 'Enter' && goToCharacter(character.id)}
									>
										<div
											class="relative rounded-lg overflow-hidden aspect-[2/3] bg-gray-200 dark:bg-gray-800"
										>
											<img
												alt={character.name}
												class="object-cover absolute inset-0 w-full h-full"
												src={character.imageUrl}
											/>

											<div
												class="w-full h-2/5 absolute bottom-0 bg-gradient-to-b from-transparent to-black/80"
											></div>

											<div class="flex absolute bottom-0 w-full p-2.5 items-end gap-1">
												<p class="text-3xl font-semibold text-white leading-none">
													{character.rank}
												</p>
											</div>
										</div>
										<div class="flex flex-col gap-1 px-1">
											<p
												class="text-base font-semibold text-gray-900 dark:text-gray-100 break-all line-clamp-2"
											>
												{character.name}
											</p>
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
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
