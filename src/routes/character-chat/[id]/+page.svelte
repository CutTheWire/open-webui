<script lang="ts">
	import { onMount, tick, getContext } from 'svelte';
	import Markdown from '$lib/components/chat/Messages/Markdown.svelte';
	import ModelSelector from '$lib/components/chat/ModelSelector.svelte';
	import { models, settings } from '$lib/stores';
	import { generateOpenAIChatCompletion } from '$lib/apis/openai';
	import { queryMemory, addNewMemory } from '$lib/apis/memories';

	const i18n = getContext('i18n');

	let messages: { id: string; role: 'user' | 'assistant'; content: string }[] = [];
	let inputMessage = '';
	let isLoading = false;
	let error: string | null = null;
	let chatContainer: HTMLElement;

	// Settings State
	let showSettings = false;
	let activeTab: 'userNote' | 'memoryBook' = 'userNote';

	let selectedModels = [''];
	let systemPrompt =
		'당신은 훌륭한 AI 연기자입니다. 주어진 페르소나와 상황에 완전히 몰입하여 대화하세요.';

	// User Note
	let userNote = '';

	import { page } from '$app/stores';

	// Persona
	let persona = {
		type: 'character',
		name: '',
		gender: '',
		age: '',
		details: '',
		prompt: ''
	};

	const PREDEFINED_CHARACTERS: Record<
		string,
		{ name: string; gender: string; age: string; details: string }
	> = {
		'1': {
			name: '들어오면 만지게 해줄게',
			gender: '여성',
			age: '20대',
			details: '사용자를 유혹하는 성격. 거침없는 말투.'
		},
		'2': {
			name: '아카데미는 힘이 곧 매력',
			gender: '여성',
			age: '10대',
			details: '아카데미의 힘을 숭배하는 캐릭터. 무뚝뚝하지만 다정한 말투.'
		},
		'3': {
			name: '언제나 웃는 마을버스 R',
			gender: '여성',
			age: '20대',
			details: '언제나 친절하게 웃는 캐릭터. 상냥한 말투.'
		},
		'4': {
			name: '혼수상태 여동생',
			gender: '여성',
			age: '10대',
			details: '여동생 캐릭터. 소심하지만 오빠를 의지하는 성격.'
		},
		'5': {
			name: '육상부 여신 타락일지',
			gender: '여성',
			age: '10대',
			details: '육상부 에이스. 자신만만하고 활기찬 성격.'
		},
		'6': {
			name: '！우당탕탕！ 콘코르디아 아카데미 U',
			gender: '여성',
			age: '10대',
			details: '활발하고 시끄러운 성격. 장난기 많은 말투.'
		}
	};

	// Memory Book
	let useMemoryBook = false;

	async function scrollToBottom() {
		await tick();
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	}

	async function processMemory(userText: string, assistantResponse?: string) {
		if (!useMemoryBook) return '';

		try {
			if (assistantResponse) {
				// Store the exchange in memory
				await addNewMemory(localStorage.token, `사용자: ${userText}\n캐릭터: ${assistantResponse}`);
				return '';
			} else {
				// Query past memories based on user input
				const memories = await queryMemory(localStorage.token, userText);
				if (memories && memories.documents && memories.documents.length > 0) {
					const relevantMemories = memories.documents[0].join('\n');
					return `[과거의 관련 기억 (메모리북)]\n${relevantMemories}\n\n위 기억을 참고하여 자연스럽게 대화를 이어가세요.`;
				}
			}
		} catch (err) {
			console.error('Memory processing error:', err);
		}
		return '';
	}

	async function sendMessage() {
		if (!inputMessage.trim() || isLoading) return;

		const userText = inputMessage;
		inputMessage = '';
		isLoading = true;
		error = null;

		// Add user message
		messages = [
			...messages,
			{
				id: crypto.randomUUID(),
				role: 'user',
				content: userText
			}
		];
		await scrollToBottom();

		try {
			// Query memory if enabled
			const memoryContext = await processMemory(userText);

			// Build the comprehensive system prompt
			let finalSystemPrompt = systemPrompt;

			if (persona.name || persona.details) {
				finalSystemPrompt += `\n\n[당신의 페르소나 설정]\n`;
				if (persona.name) finalSystemPrompt += `- 이름: ${persona.name}\n`;
				if (persona.gender) finalSystemPrompt += `- 성별: ${persona.gender}\n`;
				if (persona.age) finalSystemPrompt += `- 나이: ${persona.age}\n`;
				if (persona.details) finalSystemPrompt += `- 세부설정: ${persona.details}\n`;
			}

			if (userNote.trim()) {
				finalSystemPrompt += `\n\n[유저 노트 / 특별 지시사항]\n${userNote}`;
			}

			if (memoryContext) {
				finalSystemPrompt += `\n\n${memoryContext}`;
			}

			// Prepare messages for API
			let apiMessages = [{ role: 'system', content: finalSystemPrompt }];

			// If memory book is used, we might only send recent context to save tokens,
			// but for now we send the whole history
			apiMessages.push(...messages.map((m) => ({ role: m.role, content: m.content })));

			const modelId = selectedModels[0] || ($models && $models.length > 0 ? $models[0].id : '');

			if (!modelId) {
				throw new Error('모델이 선택되지 않았습니다.');
			}

			const response = await generateOpenAIChatCompletion(localStorage.token, {
				model: modelId,
				messages: apiMessages
			});

			if (response && response.choices && response.choices.length > 0) {
				const assistantContent = response.choices[0].message.content;
				messages = [
					...messages,
					{
						id: crypto.randomUUID(),
						role: 'assistant',
						content: assistantContent
					}
				];

				// Save interaction to memory if enabled
				await processMemory(userText, assistantContent);
			} else {
				throw new Error('API에서 올바른 응답을 받지 못했습니다.');
			}

			await scrollToBottom();
		} catch (err) {
			error = err instanceof Error ? err.message : '메시지 전송에 실패했습니다.';
			console.error('Error sending message:', err);
			messages = [
				...messages,
				{
					id: crypto.randomUUID(),
					role: 'assistant',
					content: `오류가 발생했습니다: ${error}`
				}
			];
			await scrollToBottom();
		} finally {
			isLoading = false;
		}
	}

	async function copyToClipboard(text: string) {
		try {
			await navigator.clipboard.writeText(text);
		} catch (err) {
			console.error('Failed to copy text:', err);
		}
	}

	onMount(() => {
		if ($settings?.models) {
			selectedModels = $settings.models;
		}

		const id = $page.params.id;
		if (id) {
			getCharacterById(localStorage.token, id)
				.then((data) => {
					if (data) {
						persona = data;
					}
				})
				.catch((err) => console.error('Failed to load character', err));
		}
	});
</script>

<div class="flex flex-col h-screen w-full bg-gray-50 dark:bg-gray-900">
	<div class="flex flex-col w-full h-full items-center">
		<div class="flex flex-col w-full max-w-[768px] h-full relative">
			<div
				class="w-full flex flex-col items-center pt-5 pb-7 shrink-0 z-10 bg-gradient-to-b from-gray-50 to-transparent dark:from-gray-900 absolute top-0"
			>
				{#if persona.name}
					<h1 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">{persona.name}</h1>
				{/if}
				<span class="text-xs font-medium text-gray-500"
					>이 대화는 AI로 생성된 가상의 이야기입니다</span
				>
				<button
					class="mt-2 text-sm text-blue-500 hover:underline flex items-center gap-1"
					on:click={() => (showSettings = !showSettings)}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="w-4 h-4"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.99l1.005.828c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z"
						/>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
						/>
					</svg>
					채팅방 설정 {showSettings ? '닫기' : '열기'}
				</button>
			</div>

			<div
				bind:this={chatContainer}
				class="flex flex-col w-full gap-10 flex-1 overflow-y-auto px-5 sm:px-10 pt-24 pb-32 scroll-smooth"
			>
				{#if showSettings}
					<div
						class="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 mt-2 mb-4"
					>
						<div
							class="flex flex-wrap gap-2 mb-6 border-b border-gray-200 dark:border-gray-700 pb-2"
						>
							<button
								class="px-3 py-2 text-sm font-medium {activeTab === 'userNote'
									? 'text-blue-600 border-b-2 border-blue-600'
									: 'text-gray-500 hover:text-gray-700'}"
								on:click={() => (activeTab = 'userNote')}>유저노트</button
							>
							<button
								class="px-3 py-2 text-sm font-medium {activeTab === 'memoryBook'
									? 'text-blue-600 border-b-2 border-blue-600'
									: 'text-gray-500 hover:text-gray-700'}"
								on:click={() => (activeTab = 'memoryBook')}>메모리북</button
							>
						</div>

						<div class="min-h-[200px]">
							{#if activeTab === 'userNote'}
								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										유저노트 (특별 지시문)
									</label>
									<p class="text-xs text-gray-500 mb-3">
										AI가 대화 중에 항상 참고해야 할 특별한 규칙이나 지시사항을 작성하세요.
									</p>
									<textarea
										bind:value={userNote}
										rows="6"
										class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-xl px-4 py-3 text-sm outline-none resize-y text-gray-900 dark:text-gray-100"
										placeholder="예: 항상 3줄 이내로 짧게 대답해. 나를 '마스터'라고 불러."
									></textarea>
								</div>
							{:else if activeTab === 'memoryBook'}
								<div>
									<div
										class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800"
									>
										<div>
											<label class="font-medium text-gray-900 dark:text-gray-100 block"
												>메모리북 활성화</label
											>
											<span class="text-xs text-gray-500"
												>대화 내용을 벡터 DB에 기록하고, 필요할 때 관련된 기억을 꺼내어 LLM에게
												전달합니다. (장기 기억)</span
											>
										</div>
										<label class="relative inline-flex items-center cursor-pointer">
											<input type="checkbox" bind:checked={useMemoryBook} class="sr-only peer" />
											<div
												class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
											></div>
										</label>
									</div>
									{#if useMemoryBook}
										<div
											class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 text-sm rounded-lg"
										>
											<strong>안내:</strong> 활성화 시 사용자와 캐릭터의 대화가 메모리 시스템에 자동 저장됩니다.
											대화가 길어져도 예전 중요한 기억들을 잊지 않고 참고할 수 있습니다.
										</div>
									{/if}
								</div>
							{/if}
						</div>
					</div>
				{/if}

				{#each messages as message (message.id)}
					<div class="w-full" data-message-group-id={message.id}>
						<div class="flex flex-col gap-2 relative w-full items-start">
							<div class="flex flex-row gap-4 w-full items-end justify-between">
								<div class="flex flex-col gap-2 w-full">
									<div
										class="flex flex-col gap-2 w-full break-all px-0 py-0 rounded-none bg-transparent"
									>
										<div class="text-gray-800 dark:text-gray-100">
											{#if message.role === 'user'}
												<div
													class="bg-blue-600 text-white p-4 rounded-2xl ml-auto w-fit max-w-[85%] shadow-sm"
												>
													<p class="whitespace-pre-wrap">{message.content}</p>
												</div>
											{:else}
												<!-- Character/Assistant message styling matching snippet -->
												<div class="wrtn-markdown css-68rzk4 prose dark:prose-invert max-w-none">
													<Markdown id={message.id} content={message.content} done={true} />
												</div>
											{/if}
										</div>
									</div>

									{#if message.role === 'assistant'}
										<div class="flex items-center justify-between mt-2">
											<div class="flex items-center space-x-3">
												<button
													class="relative inline-flex items-center justify-center overflow-hidden whitespace-nowrap rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 disabled:opacity-50 size-7 bg-transparent hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-500"
													type="button"
													title="복사하기"
													on:click={() => copyToClipboard(message.content)}
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														fill="currentColor"
														viewBox="0 0 24 24"
														width="18px"
														height="18px"
													>
														<path
															fill-rule="evenodd"
															d="m17.01 2.2-.25.75-2.18.72A1.4 1.4 0 0 0 13.61 5c0 .6.39 1.14.97 1.33l2.18.72.72 2.18c.19.57.73.96 1.33.96s1.14-.38 1.33-.96l.72-2.18.69-.23v13.54c0 .8-.65 1.44-1.44 1.44H3.88c-.8 0-1.44-.65-1.44-1.44V3.63a1 1 0 0 1 .08-.44l.03-.09c.21-.52.73-.9 1.33-.9zm.09 8.88a1 1 0 0 0-1.34.03l-4.56 4.34-2.94-2.28a1 1 0 0 0-1.28.05l-2.93 2.64v4.34h15.9v-6.67zM8.14 6.19a1.58 1.58 0 0 0 0 3.16 1.58 1.58 0 0 0 0-3.16"
															clip-rule="evenodd"
														/>
														<path
															d="M18.63 1.44c.06-.17.3-.17.35 0l.82 2.57 2.57.82c.17.06.17.3 0 .35L19.8 6l-.82 2.57c-.06.17-.3.17-.35 0L17.8 6l-2.57-.82c-.17-.06-.17-.3 0-.35l2.57-.82z"
														/>
													</svg>
												</button>
											</div>
											<div class="flex flex-row gap-2 items-center">
												<button
													class="relative inline-flex items-center justify-center overflow-hidden whitespace-nowrap rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 disabled:opacity-50 size-7 bg-transparent hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-400"
													type="button"
													aria-label="메시지 옵션"
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														fill="currentColor"
														viewBox="0 0 24 24"
														width="20px"
														height="20px"
													>
														<path
															d="M7.04 10.73H4.5v2.54h2.54zm6.23 0h-2.54v2.54h2.54zm3.73 0h2.54v2.54H17z"
														/>
													</svg>
												</button>
											</div>
										</div>
									{/if}
								</div>
							</div>
						</div>
					</div>
				{/each}

				{#if isLoading}
					<div class="flex items-center gap-2 text-gray-500 px-2 py-4">
						<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
						<div
							class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
							style="animation-delay: 0.2s"
						></div>
						<div
							class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
							style="animation-delay: 0.4s"
						></div>
						<span class="text-sm ml-2">Character is typing...</span>
					</div>
				{/if}
				{#if error}
					<div class="text-red-500 text-sm text-center py-2">{error}</div>
				{/if}
			</div>

			<div
				class="w-full shrink-0 px-5 sm:px-10 pb-6 pt-2 bg-gradient-to-t from-gray-50 to-transparent dark:from-gray-900 absolute bottom-0 left-0 right-0"
			>
				<div
					class="flex gap-3 bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-2 items-end"
				>
					<textarea
						bind:value={inputMessage}
						placeholder="메시지를 입력하세요..."
						on:keydown={(event) => {
							if (event.key === 'Enter' && !event.shiftKey) {
								event.preventDefault();
								sendMessage();
							}
						}}
						rows="1"
						class="flex-1 bg-transparent border-none px-4 py-3 text-sm outline-none resize-none max-h-32 text-gray-900 dark:text-gray-100 placeholder-gray-400"
						style="min-height: 44px; field-sizing: content;"
					></textarea>
					<button
						on:click={sendMessage}
						disabled={!inputMessage.trim() || isLoading}
						class="bg-black dark:bg-white text-white dark:text-black rounded-xl p-3 flex items-center justify-center transition-colors disabled:opacity-30 disabled:cursor-not-allowed hover:bg-gray-800 dark:hover:bg-gray-200"
						aria-label="전송"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="2"
							stroke="currentColor"
							class="w-5 h-5"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M6 12L3.269 3.125A59.769 59.769 0 0121.485 12 59.768 59.768 0 013.27 20.875L5.999 12Zm0 0h7.5"
							/>
						</svg>
					</button>
				</div>
				<div class="text-center mt-3">
					<span class="text-[10px] text-gray-400"
						>AI는 부정확한 정보를 제공할 수 있습니다. 중요한 정보는 확인이 필요합니다.</span
					>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	/* Any custom scrollbar styling if needed */
	.scroll-smooth {
		scroll-behavior: smooth;
	}

	/* A simple textarea auto-resize trick fallback if field-sizing isn't supported */
	textarea {
		min-height: 44px;
	}
</style>
