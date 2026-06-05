<script lang="ts">
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

		type ImageItem = {
			filename: string;
			size?: number;
			created?: number;
		};

		const API_BASE = '/api/v1/images';

		let gallery: ImageItem[] = [];
		let imageCount = 0;
		let totalSize = 0;
		let renameModalVisible = false;
		let currentRenameFile: string | null = null;
		let currentRenameExtension = 'jpg';
		let newFileName = '';
		let isLoading = false;
		let toastMessage = '';
		let toastType: 'success' | 'error' = 'success';
		let toastVisible = false;
		let fileInput: HTMLInputElement | null = null;
		let token = '';

		onMount(() => {
			token = browser ? localStorage.getItem('token') ?? '' : '';
			loadImages();
			const interval = setInterval(loadImages, 30000);
			return () => clearInterval(interval);
		});

		function authHeaders(extraHeaders: Record<string, string> = {}) {
			return {
				Authorization: `Bearer ${token}`,
				...extraHeaders
			};
		}

		async function loadImages() {
			try {
				const response = await fetch(`${API_BASE}/repository/list`, {
					headers: authHeaders({ Accept: 'application/json' })
				});

				if (!response.ok) {
					throw new Error('Failed to load images');
				}

				const data = await response.json();
				gallery = data.images || [];
				imageCount = gallery.length;
				totalSize = gallery.reduce((sum, img) => sum + (img.size || 0), 0);
			} catch (error) {
				console.error('Error loading images:', error);
				showToast('이미지 목록을 불러올 수 없습니다', 'error');
			}
		}

		function goToRoot() {
			goto('/');
		}

		function handleDragOver(event: DragEvent) {
			event.preventDefault();
			if (event.dataTransfer) {
				event.dataTransfer.dropEffect = 'copy';
			}
		}

		function handleDragLeave(event: DragEvent) {
			event.preventDefault();
		}

		function handleDrop(event: DragEvent) {
			event.preventDefault();
			if (event.dataTransfer?.files) {
				uploadImages(event.dataTransfer.files);
			}
		}

		function handleFileSelect(event: Event) {
			const input = event.currentTarget as HTMLInputElement;
			if (input.files) {
				uploadImages(input.files);
				input.value = '';
			}
		}

		async function uploadImages(files: FileList) {
			if (files.length === 0) return;

			isLoading = true;
			let successCount = 0;
			let errorCount = 0;

			for (const file of Array.from(files)) {
				try {
					const formData = new FormData();
					formData.append('file', file);

					const response = await fetch(`${API_BASE}/repository/upload`, {
						method: 'POST',
						headers: authHeaders(),
						body: formData
					});

					if (response.ok) {
						successCount += 1;
					} else {
						errorCount += 1;
						console.error('Upload error:', await response.json().catch(() => null));
					}
				} catch (error) {
					errorCount += 1;
					console.error('Upload error:', error);
				}
			}

			isLoading = false;
			if (successCount > 0) {
				showToast(`${successCount}개의 이미지가 업로드되었습니다`, 'success');
				await loadImages();
			}
			if (errorCount > 0) {
				showToast(`${errorCount}개의 이미지 업로드 실패`, 'error');
			}
		}

		async function deleteImage(filename: string) {
			if (!confirm(`"${filename}" 보관함에서 삭제하시겠습니까?`)) {
				return;
			}

			try {
				const response = await fetch(`${API_BASE}/repository/${encodeURIComponent(filename)}`, {
					method: 'DELETE',
					headers: authHeaders({ Accept: 'application/json' })
				});

				if (response.ok) {
					showToast('이미지가 삭제되었습니다', 'success');
					await loadImages();
				} else {
					const error = await response.json().catch(() => null);
					showToast(error?.detail || '삭제에 실패했습니다', 'error');
				}
			} catch (error) {
				console.error('Delete error:', error);
				showToast('삭제 중 오류가 발생했습니다', 'error');
			}
		}

		function copyURL(filename: string) {
			const url = `${window.location.origin}${API_BASE}/repository/${encodeURIComponent(filename)}`;

			if (navigator.clipboard?.writeText) {
				navigator.clipboard
					.writeText(url)
					.then(() => showToast('클립보드에 주소가 복사되었습니다', 'success'))
					.catch(() => copyURLFallback(url));
			} else {
				copyURLFallback(url);
			}
		}

		function copyURLFallback(url: string) {
			const textarea = document.createElement('textarea');
			textarea.value = url;
			textarea.style.position = 'fixed';
			textarea.style.opacity = '0';
			document.body.appendChild(textarea);
			textarea.focus();
			textarea.select();

			try {
				document.execCommand('copy');
				showToast('클립보드에 주소가 복사되었습니다', 'success');
			} catch {
				showToast('복사에 실패했습니다', 'error');
			} finally {
				document.body.removeChild(textarea);
			}
		}

		function openRenameModal(filename: string) {
			currentRenameFile = filename;
			const lastDotIndex = filename.lastIndexOf('.');
			if (lastDotIndex > 0) {
				newFileName = filename.substring(0, lastDotIndex);
				currentRenameExtension = filename.substring(lastDotIndex + 1).toLowerCase();
			} else {
				newFileName = filename;
				currentRenameExtension = 'jpg';
			}
			renameModalVisible = true;
		}

		function closeRenameModal() {
			renameModalVisible = false;
			currentRenameFile = null;
			newFileName = '';
			currentRenameExtension = 'jpg';
		}

		async function confirmRename() {
			if (!currentRenameFile) return;

			const trimmedName = newFileName.trim();
			if (!trimmedName) {
				showToast('새 파일명을 입력하세요', 'error');
				return;
			}

			if (trimmedName.includes('.')) {
				showToast('확장자는 제외하고 입력해 주세요', 'error');
				return;
			}

			const fullNewFilename = `${trimmedName}.${currentRenameExtension}`;
			if (fullNewFilename === currentRenameFile) {
				showToast('현재 이름과 동일합니다', 'error');
				return;
			}

			try {
				const response = await fetch(
					`${API_BASE}/repository/${encodeURIComponent(currentRenameFile)}/rename`,
					{
						method: 'POST',
						headers: authHeaders({ 'Content-Type': 'application/json', Accept: 'application/json' }),
						body: JSON.stringify({ new_filename: fullNewFilename })
					}
				);

				if (response.ok) {
					showToast('이미지 이름이 수정되었습니다', 'success');
					closeRenameModal();
					await loadImages();
				} else {
					const error = await response.json().catch(() => null);
					showToast(error?.detail || '이름 수정 실패', 'error');
				}
			} catch (error) {
				console.error('Rename error:', error);
				showToast('이름 수정 중 오류가 발생했습니다', 'error');
			}
		}

		function showToast(message: string, type: 'success' | 'error' = 'success') {
			toastMessage = message;
			toastType = type;
			toastVisible = true;
			setTimeout(() => {
				toastVisible = false;
			}, 3000);
		}

		function formatFileSize(bytes = 0) {
			if (bytes === 0) return '0 Bytes';
			const k = 1024;
			const sizes = ['Bytes', 'KB', 'MB', 'GB'];
			const i = Math.floor(Math.log(bytes) / Math.log(k));
			return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`;
		}

		function formatDate(timestamp?: number) {
			if (!timestamp) return '-';
			return new Date(timestamp * 1000).toLocaleDateString('ko-KR');
		}

		function handleImageError(event: Event) {
			const target = event.currentTarget as HTMLImageElement;
			target.src =
				"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='240'><rect width='100%25' height='100%25' fill='%23202020'/><text x='50%25' y='50%25' fill='%23888' text-anchor='middle' dy='.3em' font-size='16'>이미지 로드 실패</text></svg>";
		}
	</script>

	<svelte:head>
		<title>이미지 저장소</title>
	</svelte:head>

	<div class="page-shell">
		<div class="app-layout">
			<aside class="sidebar-panel">
				<div class="header">
					<h1>이미지 저장소</h1>
					<p>Open WebUI Images Storage</p>
				</div>

				<button class="nav-button" on:click={goToRoot}>
					<img class="sidebar-new-chat-icon size-6 rounded-full" alt="" src="/static/favicon.png" />
					<span>Open WebUI</span>
				</button>

				<div class="stats" id="stats">
					<div class="stat-card">
						<span class="label">전체 이미지</span>
						<span class="value">{imageCount}</span>
					</div>
					<div class="stat-card">
						<span class="label">사용 중인 용량</span>
						<span class="value">{formatFileSize(totalSize)}</span>
					</div>
				</div>

				<div class="section">
					<h2>파일 업로드</h2>
					<div
						class="upload-area"
						on:click={() => fileInput?.click()}
						on:dragover={handleDragOver}
						on:dragleave={handleDragLeave}
						on:drop={handleDrop}
					>
						<div class="upload-icon">＋</div>
						<p>클릭하거나 드래그하여 업로드</p>
						<p class="upload-note">JPG, PNG, GIF, WebP (최대 50MB)</p>
					</div>
					<input
						bind:this={fileInput}
						type="file"
						accept="image/*"
						multiple
						on:change={handleFileSelect}
					/>
				</div>
			</aside>

			<main class="main-panel">
				<div class="section">
					<h2>저장된 이미지 목록</h2>

					{#if isLoading}
						<div class="loading">업로드 처리 중...</div>
					{:else if gallery.length === 0}
						<div class="empty-state">
							<div class="icon">📁</div>
							<p>보관함이 비어 있습니다.</p>
						</div>
					{:else}
						<div class="gallery">
							{#each gallery as image (image.filename)}
								<div class="image-card">
									<div class="image-preview">
										<img
											src={`${API_BASE}/repository/${encodeURIComponent(image.filename)}`}
											alt={image.filename}
											loading="lazy"
											on:error={handleImageError}
										/>
									</div>
									<div class="image-info">
										<div class="image-name" title={image.filename}>{image.filename}</div>
										<div class="image-size">{formatFileSize(image.size || 0)}</div>
										<div class="image-date">{formatDate(image.created)}</div>
										<div class="image-actions">
											<button class="btn-copy" on:click={() => copyURL(image.filename)}>복사</button>
											<button class="btn-rename" on:click={() => openRenameModal(image.filename)}>수정</button>
											<button class="btn-delete" on:click={() => deleteImage(image.filename)}>삭제</button>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</main>
		</div>
	</div>

	{#if renameModalVisible}
		<div class="modal-backdrop" on:click={closeRenameModal}>
			<div class="modal-content" on:click|stopPropagation>
				<div class="modal-header">이미지 이름 변경</div>
				<div class="modal-body">
					<label>현재 파일명</label>
					<div class="readonly-field">{currentRenameFile}</div>

					<label>새 파일명 (확장자 제외)</label>
					<input type="text" bind:value={newFileName} placeholder="변경할 파일명을 입력하세요" maxlength="200" />

					<label>파일 형식 확장자</label>
					<select bind:value={currentRenameExtension}>
						<option value="jpg">JPG (.jpg)</option>
						<option value="jpeg">JPEG (.jpeg)</option>
						<option value="png">PNG (.png)</option>
						<option value="gif">GIF (.gif)</option>
						<option value="webp">WebP (.webp)</option>
						<option value="bmp">BMP (.bmp)</option>
					</select>
				</div>
				<div class="modal-footer">
					<button class="btn-modal-cancel" on:click={closeRenameModal}>취소</button>
					<button class="btn-modal-confirm" on:click={confirmRename}>이름 변경</button>
				</div>
			</div>
		</div>
	{/if}

	{#if toastVisible}
		<div class={`toast ${toastType}`}>{toastMessage}</div>
	{/if}

	<style>
		:global(body) {
			margin: 0;
			min-height: 100vh;
			background:
				radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 28%),
				linear-gradient(180deg, #111111 0%, #0a0a0a 100%);
			color: #ececec;
		}

		.page-shell {
			min-height: 100vh;
		}

		.app-layout {
			display: flex;
			width: 100%;
			min-height: 100vh;
		}

		.sidebar-panel {
			width: 320px;
			background: #0d0d0d;
			border-right: 1px solid #272727;
			padding: 24px;
			display: flex;
			flex-direction: column;
			gap: 20px;
		}

		.main-panel {
			flex: 1;
			padding: 40px;
			overflow-y: auto;
			max-width: 1400px;
			margin: 0 auto;
			width: 100%;
		}

		.header h1 {
			font-size: 24px;
			font-weight: 700;
			margin: 0 0 6px;
			display: flex;
			align-items: center;
			gap: 8px;
		}

		.header p {
			font-size: 14px;
			color: #b4b4b4;
			margin: 0;
		}

		.nav-button {
			display: flex;
			align-items: center;
			gap: 12px;
			width: 100%;
			padding: 12px 16px;
			background: #2f2f2f;
			border: 1px solid #333;
			border-radius: 10px;
			color: #ececec;
			font-size: 14px;
			font-weight: 500;
			cursor: pointer;
			transition: all 0.15s ease;
			text-align: left;
		}

		.nav-button:hover {
			background: #3d3d3d;
			border-color: #444;
		}

		.sidebar-new-chat-icon {
			display: block;
			flex-shrink: 0;
			object-fit: cover;
		}

		.size-6 {
			width: 24px;
			height: 24px;
		}

		.rounded-full {
			border-radius: 9999px;
		}

		.stats {
			display: flex;
			flex-direction: column;
			gap: 12px;
		}

		.stat-card {
			background: #202020;
			border: 1px solid #333;
			padding: 16px;
			border-radius: 10px;
			display: flex;
			justify-content: space-between;
			align-items: center;
		}

		.stat-card .label {
			font-size: 13px;
			color: #b4b4b4;
		}

		.stat-card .value {
			font-size: 18px;
			font-weight: 700;
			color: #ececec;
		}

		.section h2 {
			font-size: 18px;
			font-weight: 600;
			margin: 0 0 16px;
			color: #ececec;
		}

		.upload-area {
			border: 2px dashed #333;
			border-radius: 12px;
			padding: 32px 16px;
			text-align: center;
			cursor: pointer;
			transition: all 0.2s ease;
			background: #202020;
		}

		.upload-area:hover,
		.upload-area.dragover {
			border-color: #3b82f6;
			background: #262626;
		}

		.upload-area p {
			color: #ececec;
			font-size: 14px;
			margin: 0 0 6px;
		}

		.upload-note {
			font-size: 11px;
			color: #b4b4b4;
		}

		input[type='file'] {
			display: none;
		}

		.gallery {
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
			gap: 20px;
		}

		.image-card {
			background: #202020;
			border: 1px solid #333;
			border-radius: 12px;
			overflow: hidden;
			transition: transform 0.2s ease, border-color 0.2s ease;
			display: flex;
			flex-direction: column;
		}

		.image-card:hover {
			transform: translateY(-2px);
			border-color: #444;
		}

		.image-preview {
			width: 100%;
			height: 160px;
			background: #1a1a1a;
			display: flex;
			align-items: center;
			justify-content: center;
			overflow: hidden;
			border-bottom: 1px solid #333;
		}

		.image-preview img {
			width: 100%;
			height: 100%;
			object-fit: cover;
		}

		.image-info {
			padding: 14px;
			display: flex;
			flex-direction: column;
			flex-grow: 1;
		}

		.image-name {
			font-weight: 500;
			color: #ececec;
			word-break: break-all;
			margin-bottom: 4px;
			font-size: 13px;
			display: -webkit-box;
			-webkit-line-clamp: 1;
			line-clamp: 1;
			-webkit-box-orient: vertical;
			overflow: hidden;
		}

		.image-size,
		.image-date {
			color: #b4b4b4;
			font-size: 11px;
			margin-bottom: 8px;
		}

		.image-actions {
			display: flex;
			gap: 6px;
			margin-top: auto;
		}

		.image-actions button {
			flex: 1;
			padding: 7px;
			border: 1px solid #333;
			border-radius: 6px;
			font-size: 12px;
			font-weight: 500;
			cursor: pointer;
			background: #2f2f2f;
			color: #ececec;
			transition: background 0.15s ease, border-color 0.15s ease;
		}

		.image-actions .btn-copy:hover,
		.image-actions .btn-rename:hover {
			background: #3d3d3d;
		}

		.image-actions .btn-rename:hover {
			border-color: #3b82f6;
		}

		.image-actions .btn-delete {
			color: #f87171;
		}

		.image-actions .btn-delete:hover {
			background: #351a1a;
			border-color: #ef4444;
		}

		.empty-state,
		.loading {
			grid-column: 1 / -1;
			text-align: center;
			padding: 80px 20px;
			color: #b4b4b4;
		}

		.empty-state .icon {
			font-size: 40px;
			margin-bottom: 12px;
			opacity: 0.4;
		}

		.modal-backdrop {
			position: fixed;
			inset: 0;
			background: rgba(0, 0, 0, 0.7);
			backdrop-filter: blur(4px);
			display: flex;
			align-items: center;
			justify-content: center;
			z-index: 2000;
		}

		.modal-content {
			background: #202020;
			border: 1px solid #333;
			padding: 24px;
			border-radius: 14px;
			max-width: 440px;
			width: min(90vw, 440px);
			box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
		}

		.modal-header {
			font-size: 18px;
			font-weight: 600;
			margin-bottom: 16px;
			color: #ececec;
		}

		.modal-body label {
			display: block;
			margin-bottom: 6px;
			color: #b4b4b4;
			font-size: 12px;
		}

		.modal-body input,
		.modal-body select {
			width: 100%;
			padding: 10px 12px;
			background: #2f2f2f;
			border: 1px solid #333;
			border-radius: 8px;
			font-size: 14px;
			color: #ececec;
			margin-bottom: 14px;
		}

		.modal-body input:focus,
		.modal-body select:focus {
			outline: none;
			border-color: #3b82f6;
		}

		.readonly-field {
			padding: 10px;
			background: #1a1a1a;
			border: 1px solid #333;
			border-radius: 6px;
			margin-bottom: 14px;
			font-size: 13px;
			color: #b4b4b4;
			word-break: break-all;
		}

		.modal-footer {
			display: flex;
			gap: 8px;
			justify-content: flex-end;
			margin-top: 20px;
		}

		.modal-footer button {
			padding: 9px 16px;
			border: none;
			border-radius: 8px;
			font-size: 14px;
			font-weight: 500;
			cursor: pointer;
		}

		.btn-modal-cancel {
			background: #2f2f2f;
			color: #ececec;
		}

		.btn-modal-cancel:hover {
			background: #3d3d3d;
		}

		.btn-modal-confirm {
			background: #3b82f6;
			color: white;
		}

		.btn-modal-confirm:hover {
			background: #2563eb;
		}

		.toast {
			position: fixed;
			bottom: 24px;
			right: 24px;
			padding: 12px 20px;
			border-radius: 8px;
			color: white;
			font-size: 14px;
			font-weight: 500;
			box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
			z-index: 3000;
			display: flex;
			align-items: center;
			gap: 8px;
		}

		.toast.success {
			background: #10b981;
		}

		.toast.error {
			background: #ef4444;
		}

		::-webkit-scrollbar {
			width: 8px;
			height: 8px;
		}

		::-webkit-scrollbar-track {
			background: transparent;
		}

		::-webkit-scrollbar-thumb {
			background: #333;
			border-radius: 999px;
		}

		::-webkit-scrollbar-thumb:hover {
			background: #444;
		}

		@media (max-width: 900px) {
			.app-layout {
				flex-direction: column;
			}

			.sidebar-panel {
				width: 100%;
				border-right: 0;
				border-bottom: 1px solid #272727;
			}

			.main-panel {
				padding: 24px;
			}
		}
	</style>
