/**
 * StoryForge AI - Static Demo Version
 * Same UI, no backend required. Questions hardcoded, demo story generation.
 */

class StoryForgeApp {
    constructor() {
        // Core state
        this.sessionId = 'static-' + Date.now();
        this.currentQuestionId = null;
        this.currentPhase = 'setting';
        this.questionIndex = 0;
        this.responses = {};
        this.storySegments = [];
        this.isGenerating = false;

        // Enhanced state
        this.theme = localStorage.getItem('storyforge-theme') || 'dark';
        this.bookmarks = JSON.parse(localStorage.getItem('storyforge-bookmarks') || '[]');
        this.savedStories = JSON.parse(localStorage.getItem('storyforge-stories') || '[]');
        this.storyHistory = [];
        this.currentChapter = 1;
        this.undoStack = [];
        this.redoStack = [];
        this.isReadingMode = false;
        this.isTypingEnabled = true;
        this.isSoundEnabled = localStorage.getItem('storyforge-sound') !== 'false';
        this.currentMood = 'neutral';
        this.characters = [];

        this.audioContext = null;
        this.ambientSound = null;

        this.phaseNames = {
            'setting': '🌍 World Building',
            'character': '👤 Characters',
            'theme': '🎭 Theme & Genre',
            'plot': '📖 Plot Structure',
            'continuation': '✨ Story Time'
        };

        this.moodThemes = {
            'neutral': { color: '#6366f1', icon: '😐', sound: 'ambient' },
            'happy': { color: '#22c55e', icon: '😊', sound: 'upbeat' },
            'sad': { color: '#3b82f6', icon: '😢', sound: 'melancholy' },
            'tense': { color: '#ef4444', icon: '😰', sound: 'suspense' },
            'romantic': { color: '#ec4899', icon: '💕', sound: 'romantic' },
            'mysterious': { color: '#8b5cf6', icon: '🔮', sound: 'mystery' },
            'adventurous': { color: '#f59e0b', icon: '⚔️', sound: 'adventure' }
        };

        // Hardcoded questions database
        this.questionsDB = this._initQuestions();
        this.questionOrder = this._buildQuestionOrder();

        this.init();
    }

    _initQuestions() {
        return {
            setting_1: {
                id: "setting_1", phase: "setting",
                text: "Where should this story take place?",
                options: [
                    "A magical fantasy realm with castles and dragons",
                    "A futuristic sci-fi world with advanced technology",
                    "The real modern world we live in",
                    "A historical setting from the past",
                    "A mysterious supernatural dimension"
                ]
            },
            setting_2: {
                id: "setting_2", phase: "setting",
                text: "What time period appeals to you for this story?",
                options: [
                    "Ancient times (medieval, mythological)",
                    "Historical past (Victorian, Renaissance, etc.)",
                    "Present day (contemporary)",
                    "Near future (next 50-100 years)",
                    "Distant future (space age, post-apocalyptic)"
                ]
            },
            setting_3: {
                id: "setting_3", phase: "setting",
                text: "What kind of atmosphere do you prefer?",
                options: [
                    "Dark and mysterious",
                    "Bright and adventurous",
                    "Romantic and emotional",
                    "Comedic and lighthearted",
                    "Thrilling and suspenseful"
                ]
            },
            setting_4: {
                id: "setting_4", phase: "setting",
                text: "Are there any specific locations you'd like featured?",
                options: [
                    "Bustling cities and urban environments",
                    "Enchanted forests and natural landscapes",
                    "Space stations or alien planets",
                    "Underwater kingdoms or oceanic adventures",
                    "Mountains, caves, or underground realms"
                ]
            },
            char_1: {
                id: "char_1", phase: "character",
                text: "What should be the name of your main character? (Type your answer)",
                options: null
            },
            char_2: {
                id: "char_2", phase: "character",
                text: "What personality traits should your main character have?",
                options: [
                    "Brave and courageous",
                    "Clever and witty",
                    "Kind and compassionate",
                    "Mysterious and secretive",
                    "Rebellious and independent"
                ]
            },
            char_3: {
                id: "char_3", phase: "character",
                text: "What motivates your character?",
                options: [
                    "Love and relationships",
                    "Revenge or justice",
                    "Curiosity and discovery",
                    "Duty and responsibility",
                    "Survival and protection",
                    "Redemption and forgiveness"
                ]
            },
            char_4: {
                id: "char_4", phase: "character",
                text: "Should there be companions or allies? What kind?",
                options: [
                    "A loyal best friend",
                    "A wise mentor figure",
                    "A group of diverse companions",
                    "A mysterious stranger who helps",
                    "A magical creature or pet",
                    "The character journeys alone"
                ]
            },
            char_5: {
                id: "char_5", phase: "character",
                text: "What kind of antagonist or obstacle should your character face?",
                options: [
                    "A powerful villain with dark motives",
                    "A corrupt organization or government",
                    "Forces of nature or supernatural threats",
                    "Internal struggles and personal demons",
                    "A rival with conflicting goals",
                    "An ancient evil awakening"
                ]
            },
            theme_1: {
                id: "theme_1", phase: "theme",
                text: "What genre best describes your ideal story?",
                options: [
                    "Fantasy (magic, mythical creatures)",
                    "Science Fiction (technology, space)",
                    "Mystery (puzzles, detective work)",
                    "Romance (love stories, relationships)",
                    "Thriller (suspense, action)",
                    "Adventure (quests, exploration)"
                ]
            },
            theme_2: {
                id: "theme_2", phase: "theme",
                text: "What emotional journey should the story take?",
                options: [
                    "Uplifting and inspiring",
                    "Bittersweet with mixed emotions",
                    "Thrilling and exciting",
                    "Thought-provoking and philosophical",
                    "Heartwarming and comforting"
                ]
            },
            theme_3: {
                id: "theme_3", phase: "theme",
                text: "Are there themes you'd like explored?",
                options: [
                    "Friendship and loyalty",
                    "Sacrifice and heroism",
                    "Identity and self-discovery",
                    "Power and corruption",
                    "Nature and environment",
                    "Technology and humanity"
                ]
            },
            theme_4: {
                id: "theme_4", phase: "theme",
                text: "What tone do you prefer for the narrative?",
                options: [
                    "Serious and dramatic",
                    "Lighthearted and fun",
                    "Dark and intense",
                    "Humorous with witty dialogue",
                    "Philosophical and reflective"
                ]
            },
            plot_1: {
                id: "plot_1", phase: "plot",
                text: "What kind of conflict should drive the story?",
                options: [
                    "Person vs. Person (battles, rivalries)",
                    "Person vs. Nature (survival, disasters)",
                    "Person vs. Self (inner struggles)",
                    "Person vs. Society (rebellion, justice)",
                    "Person vs. Supernatural (magic, gods)"
                ]
            },
            plot_2: {
                id: "plot_2", phase: "plot",
                text: "Do you prefer action-heavy plots or character-driven stories?",
                options: [
                    "Action-heavy with lots of excitement",
                    "Character-driven with deep emotions",
                    "A balanced mix of both",
                    "Mystery-focused with puzzles to solve",
                    "Dialogue-heavy with witty conversations"
                ]
            },
            plot_3: {
                id: "plot_3", phase: "plot",
                text: "How complex should the plot be?",
                options: [
                    "Straightforward and easy to follow",
                    "Moderately complex with some twists",
                    "Intricate with multiple plot threads",
                    "Full of surprises and unexpected turns"
                ]
            },
            plot_4: {
                id: "plot_4", phase: "plot",
                text: "What kind of ending appeals to you?",
                options: [
                    "Happy ending where everything works out",
                    "Bittersweet with some sacrifice",
                    "Ambiguous, leaving some mystery",
                    "Open-ended for continuation",
                    "Unexpected twist ending"
                ]
            }
        };
    }

    _buildQuestionOrder() {
        return [
            'setting_1','setting_2','setting_3','setting_4',
            'char_1','char_2','char_3','char_4','char_5',
            'theme_1','theme_2','theme_3','theme_4',
            'plot_1','plot_2','plot_3','plot_4'
        ];
    }

    init() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.bindEvents();
        this.setStatus(true);
        this.startNewSession();
    }

    bindEvents() {
        document.getElementById('nextBtn')?.addEventListener('click', () => this.handleNext());
        document.getElementById('backBtn')?.addEventListener('click', () => this.handleBack());
        document.getElementById('newStoryBtn')?.addEventListener('click', () => this.confirmNewStory());
        document.getElementById('continueBtn')?.addEventListener('click', () => this.showContinueOptions());
        document.getElementById('downloadBtn')?.addEventListener('click', () => this.showExportOptions());
        document.getElementById('themeToggle')?.addEventListener('click', () => this.toggleTheme());
        document.getElementById('soundToggle')?.addEventListener('click', () => this.toggleSound());
        document.getElementById('settingsBtn')?.addEventListener('click', () => this.openSettings());
        document.getElementById('closeSettings')?.addEventListener('click', () => this.closeSettings());
        document.getElementById('settingsOverlay')?.addEventListener('click', () => this.closeSettings());
        document.getElementById('saveSettings')?.addEventListener('click', () => this.saveSettings());
        document.getElementById('saveStoryBtn')?.addEventListener('click', () => this.saveCurrentStory());
        document.getElementById('loadStoryBtn')?.addEventListener('click', () => this.showLoadStories());
        document.getElementById('bookmarkBtn')?.addEventListener('click', () => this.addBookmark());
        document.getElementById('historyBtn')?.addEventListener('click', () => this.showJourney());
        document.getElementById('undoBtn')?.addEventListener('click', () => this.undo());
        document.getElementById('redoBtn')?.addEventListener('click', () => this.redo());
        document.getElementById('readingModeBtn')?.addEventListener('click', () => this.toggleReadingMode());

        const textInput = document.getElementById('textInput');
        textInput?.addEventListener('input', () => this.updateNextButtonState());
        textInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const nextBtn = document.getElementById('nextBtn');
                if (nextBtn && !nextBtn.disabled) this.handleNext();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key.toLowerCase()) {
                    case 's': e.preventDefault(); this.saveCurrentStory(); break;
                    case 'b': e.preventDefault(); this.addBookmark(); break;
                    case 'z': e.preventDefault(); this.undo(); break;
                    case 'y': e.preventDefault(); this.redo(); break;
                    case 't': e.preventDefault(); this.toggleTheme(); break;
                    case 'r': e.preventDefault(); this.toggleReadingMode(); break;
                    case 'd': e.preventDefault(); this.showExportOptions(); break;
                }
            }
            if (e.key === '?' && !e.target.matches('input, textarea')) {
                this.toggleShortcutsHint();
            }
        });

        // Temperature slider
        const tempSlider = document.getElementById('temperature');
        tempSlider?.addEventListener('input', () => {
            const val = parseFloat(tempSlider.value);
            const labels = { 0.1: 'Very Focused', 0.3: 'Focused', 0.5: 'Balanced', 0.7: 'Creative', 0.8: 'Imaginative', 0.9: 'Wild', 1.0: 'Maximum Chaos' };
            const closest = Object.keys(labels).reduce((a, b) => Math.abs(b - val) < Math.abs(a - val) ? b : a);
            document.getElementById('tempValue').textContent = `${val} - ${labels[closest]}`;
        });
    }

    setStatus(online) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        if (online) {
            statusDot?.classList.add('online');
            if (statusText) statusText.textContent = '✓ Static Demo Mode';
        } else {
            statusDot?.classList.remove('online');
            if (statusText) statusText.textContent = '⚠ Offline';
        }
    }

    confirmNewStory() {
        if (this.storySegments.length > 0) {
            const modal = this.createModal('Start New Story?', `
                <p>You have an ongoing story. Do you want to save it before starting a new one?</p>
                <div class="modal-actions">
                    <button class="btn btn-ghost" onclick="app.closeAllModals(); app.startNewSession();">Don't Save</button>
                    <button class="btn btn-primary" onclick="app.saveCurrentStory(); app.closeAllModals(); app.startNewSession();">Save & Start New</button>
                </div>
            `);
            document.body.appendChild(modal);
        } else {
            this.startNewSession();
        }
    }

    startNewSession() {
        this.sessionId = 'static-' + Date.now();
        this.responses = {};
        this.storySegments = [];
        this.questionIndex = 0;
        this.currentChapter = 1;
        this.undoStack = [];
        this.redoStack = [];
        this.storyHistory = [];
        this.characters = [];
        this.currentMood = 'neutral';

        this.showSection('question');
        this.loadNextQuestion();
        this.updateUndoRedoButtons();
        this.updateMoodIndicator('neutral');
        this.updateCharacterPanel();
        this.playSound('success');
        this.showNotification('New story session started!', 'success');
    }

    loadNextQuestion(currentId = null) {
        let nextIndex = 0;

        if (currentId !== null) {
            const currentIndex = this.questionOrder.indexOf(currentId);
            nextIndex = currentIndex + 1;
        }

        if (nextIndex >= this.questionOrder.length) {
            this.generateStory();
            return;
        }

        const questionId = this.questionOrder[nextIndex];
        const question = this.questionsDB[questionId];

        this.currentQuestionId = question.id;
        this.currentPhase = question.phase;
        this.questionIndex = nextIndex + 1;

        this.renderQuestion(question);
        this.updateProgress({
            percentage: ((nextIndex) / this.questionOrder.length) * 100,
            answered: nextIndex,
            total: this.questionOrder.length
        });
    }

    renderQuestion(question) {
        const phaseBadge = document.getElementById('phaseBadge');
        if (phaseBadge) phaseBadge.textContent = this.phaseNames[question.phase] || question.phase;

        const questionNumber = document.getElementById('questionNumber');
        if (questionNumber) questionNumber.textContent = `Question ${this.questionIndex}`;

        const questionText = document.getElementById('questionText');
        if (questionText) questionText.textContent = question.text;

        const optionsContainer = document.getElementById('optionsContainer');
        const textInputContainer = document.getElementById('textInputContainer');

        if (question.options && question.options.length > 0) {
            optionsContainer.style.display = 'grid';
            textInputContainer.classList.remove('active');
            optionsContainer.innerHTML = question.options.map((option) => `
                <button class="option-btn" data-value="${this.escapeHtml(option)}" onclick="app.selectOption(this)">
                    ${this.escapeHtml(option)}
                </button>
            `).join('');
        } else {
            optionsContainer.style.display = 'none';
            textInputContainer.classList.add('active');
            const textInput = document.getElementById('textInput');
            if (textInput) { textInput.value = ''; textInput.focus(); }
        }

        this.updateNextButtonState();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    selectOption(button) {
        document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
        button.classList.add('selected');
        this.playSound('click');
        this.updateNextButtonState();
    }

    updateNextButtonState() {
        const nextBtn = document.getElementById('nextBtn');
        if (!nextBtn) return;
        const selectedOption = document.querySelector('.option-btn.selected');
        const textInput = document.getElementById('textInput');
        const textInputContainer = document.getElementById('textInputContainer');

        let hasAnswer = false;
        if (textInputContainer?.classList.contains('active')) {
            hasAnswer = textInput?.value.trim().length > 0;
        } else {
            hasAnswer = selectedOption !== null;
        }
        nextBtn.disabled = !hasAnswer;
    }

    handleNext() {
        let answer = '';
        const selectedOption = document.querySelector('.option-btn.selected');
        const textInput = document.getElementById('textInput');
        const textInputContainer = document.getElementById('textInputContainer');

        if (textInputContainer?.classList.contains('active')) {
            answer = textInput?.value.trim() || '';
        } else if (selectedOption) {
            answer = selectedOption.dataset.value;
        }

        if (!answer) return;

        this.responses[this.currentQuestionId] = answer;
        this.playSound('click');
        this.loadNextQuestion(this.currentQuestionId);
    }

    handleBack() {
        if (this.questionIndex <= 1) return;
        const prevIndex = this.questionIndex - 2;
        const prevId = this.questionOrder[prevIndex];
        const prevQuestion = this.questionsDB[prevId];

        this.currentQuestionId = prevQuestion.id;
        this.currentPhase = prevQuestion.phase;
        this.questionIndex = prevIndex + 1;

        this.renderQuestion(prevQuestion);
        this.updateProgress({
            percentage: (prevIndex / this.questionOrder.length) * 100,
            answered: prevIndex,
            total: this.questionOrder.length
        });
        this.showNotification('Going back...', 'info');
    }

    updateProgress(progress) {
        const progressFill = document.getElementById('progressFill');
        const progressCurrent = document.getElementById('progressCurrent');
        const progressTotal = document.getElementById('progressTotal');
        if (progressFill) progressFill.style.width = `${progress.percentage}%`;
        if (progressCurrent) progressCurrent.textContent = progress.answered;
        if (progressTotal) progressTotal.textContent = progress.total;
    }

    // ==================== Demo Story Generation ====================

    async generateStory() {
        this.showLoading(true, 'Crafting your story...');

        // Simulate generation delay
        await new Promise(r => setTimeout(r, 2000));

        const story = this._buildDemoStory();

        const data = {
            content: story,
            html_content: story.split('\n\n').map(p => `<p>${p}</p>`).join(''),
            word_count: story.split(/\s+/).length,
            segment_count: 1,
            choices: [
                "Continue with more action and adventure",
                "Develop the characters and relationships",
                "Introduce a surprising twist",
                "Build towards the climax"
            ]
        };

        await this.displayStory(data);
        this.playSound('success');
        this.showNotification('Your story is ready!', 'success');
        this.showLoading(false);
    }

    _buildDemoStory() {
        const r = this.responses;
        const charName = r['char_1'] || 'The Hero';
        const setting = r['setting_1'] || 'a mysterious world';
        const atmosphere = r['setting_3'] || 'an intriguing atmosphere';
        const personality = r['char_2'] || 'brave and courageous';
        const motivation = r['char_3'] || 'curiosity and discovery';
        const companion = r['char_4'] || 'a loyal companion';
        const antagonist = r['char_5'] || 'a formidable adversary';
        const genre = r['theme_1'] || 'an epic adventure';
        const conflict = r['plot_1'] || 'a great conflict';
        const ending = r['plot_4'] || 'a satisfying conclusion';
        const timePeriod = r['setting_2'] || 'a timeless era';
        const location = r['setting_4'] || 'breathtaking landscapes';
        const emotionalJourney = r['theme_2'] || 'a thrilling journey';
        const themes = r['theme_3'] || 'friendship and loyalty';
        const tone = r['theme_4'] || 'dramatic and engaging';
        const plotStyle = r['plot_2'] || 'a balanced mix of action and emotion';
        const complexity = r['plot_3'] || 'moderately complex with twists';

        return `In ${setting.toLowerCase()}, set during ${timePeriod.toLowerCase()}, there lived ${charName} — a soul defined by being ${personality.toLowerCase()}. The world around them was filled with ${atmosphere.toLowerCase()}, where ${location.toLowerCase()} stretched as far as the eye could see.

${charName} was driven by ${motivation.toLowerCase()}, a fire that burned deep within their heart. It was this very drive that set them on a path that would change everything. Alongside them traveled ${companion.toLowerCase()}, whose presence brought both comfort and strength to the journey ahead.

The story unfolded as ${genre.toLowerCase()}, weaving threads of ${themes.toLowerCase()} into every chapter. The narrative carried ${emotionalJourney.toLowerCase()}, told in a tone that was ${tone.toLowerCase()}. Every scene was crafted with ${plotStyle.toLowerCase()}, building a tale that was ${complexity.toLowerCase()}.

But darkness loomed on the horizon. ${antagonist.charAt(0).toUpperCase() + antagonist.slice(1).toLowerCase()} stood in their way, creating ${conflict.toLowerCase()} that tested ${charName}'s resolve to its very limits. The clash between light and shadow would determine the fate of everything they held dear.

As the winds of change swept across the land, ${charName} squared their shoulders and stepped forward into the unknown. The road ahead was treacherous, but the fire of determination blazed bright. This was only the beginning — and the story promised ${ending.toLowerCase()}.

The adventure awaits. What happens next is up to you...`;
    }

    async displayStory(data) {
        this.showSection('story');
        const storyContent = document.getElementById('storyContent');
        if (storyContent) {
            storyContent.innerHTML = '';
            const chapterMarker = document.createElement('div');
            chapterMarker.className = 'chapter-marker';
            chapterMarker.innerHTML = `
                <div class="chapter-number">Chapter 1</div>
                <div class="chapter-title">The Beginning</div>
                <div class="chapter-divider"></div>
            `;
            storyContent.appendChild(chapterMarker);

            const contentDiv = document.createElement('div');
            contentDiv.className = 'story-segment';
            storyContent.appendChild(contentDiv);

            if (this.isTypingEnabled && data.content) {
                await this.typeText(contentDiv, data.html_content || `<p>${this.escapeHtml(data.content)}</p>`);
            } else {
                contentDiv.innerHTML = data.html_content || `<p>${this.escapeHtml(data.content)}</p>`;
            }
        }

        this.updateStats(data);
        this.storySegments.push(data.content);
        this.saveState();

        const mood = this.analyzeMood(data.content);
        this.updateMoodIndicator(mood);
        this.extractCharacters(data.content);

        if (data.choices?.length > 0) {
            this.displayChoices(data.choices);
        }
    }

    updateStats(data) {
        const wordCount = data?.word_count || this.storySegments.join(' ').split(/\s+/).length;
        const segmentCount = data?.segment_count || this.storySegments.length;
        document.getElementById('wordCount').textContent = wordCount;
        document.getElementById('segmentCount').textContent = segmentCount;
    }

    displayChoices(choices) {
        const storyChoices = document.getElementById('storyChoices');
        if (!storyChoices) return;

        storyChoices.innerHTML = `<div class="choices-title">What happens next?</div>`;

        choices.forEach((choice) => {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.textContent = choice;
            btn.addEventListener('click', () => this.selectChoice(choice));
            storyChoices.appendChild(btn);
        });

        const customBtn = document.createElement('button');
        customBtn.className = 'choice-btn custom-choice';
        customBtn.textContent = '✏️ Write your own direction...';
        customBtn.addEventListener('click', () => this.showCustomInput());
        storyChoices.appendChild(customBtn);

        storyChoices.style.display = 'block';
    }

    async selectChoice(choice) {
        this.saveState();
        this.addToHistory('choice', { choice });
        this.showLoading(true, 'Continuing your story...');
        this.playSound('click');

        await new Promise(r => setTimeout(r, 1500));

        const charName = this.responses['char_1'] || 'The Hero';
        const continuations = {
            "Continue with more action and adventure": `${charName} charged forward with renewed vigor, the ground trembling beneath their feet. The path ahead split into two — one leading through a treacherous mountain pass, the other descending into a mist-filled valley. Without hesitation, they chose the more dangerous route, knowing that great rewards awaited those who dared.\n\nThe clash of steel echoed through the canyon as unexpected foes emerged from the shadows. ${charName} fought with precision and grace, each movement telling the story of countless battles before. When the dust settled, a hidden doorway stood revealed in the rock face — an entrance to something ancient and powerful.`,
            "Develop the characters and relationships": `That evening, as the campfire crackled under a canopy of stars, ${charName} sat in quiet reflection. The journey had changed them in ways they hadn't expected. Old wounds began to surface, and with them, a vulnerability they rarely showed.\n\n"You don't have to carry this burden alone," came a gentle voice from across the fire. The words hung in the air like embers, warm and fleeting. For the first time in a long while, ${charName} allowed themselves to trust, to share the weight of their story. In that moment, bonds were forged stronger than any armor.`,
            "Introduce a surprising twist": `Just as ${charName} thought the path was clear, a shocking revelation shattered everything they believed. The very person they had trusted most — the one who had guided them through darkness — had been working against them all along.\n\n"Did you really think it would be that simple?" The words cut deeper than any blade. ${charName} stood frozen, the world tilting on its axis. But from the ashes of betrayal, a new truth emerged — one that would rewrite the entire story. Nothing was as it seemed, and the real journey was only now beginning.`,
            "Build towards the climax": `The final confrontation loomed ahead like a storm on the horizon. ${charName} could feel it in the air — the weight of destiny pressing down with every step. All the choices, all the sacrifices, had led to this single moment.\n\nThe fortress rose before them, dark and imposing against a blood-red sky. Inside waited the source of all the chaos, the heart of the conflict that had torn their world apart. ${charName} drew a deep breath, feeling the strength of every ally, every lesson, every trial flowing through them. "This ends now," they whispered, and stepped through the gates.`
        };

        const content = continuations[choice] || `${charName} considered the path ahead carefully. "${choice}" — the words echoed in their mind as they made their decision. The world responded to their choice, shifting and reshaping around them as new possibilities emerged.\n\nThe journey continued, each step revealing new wonders and challenges. Whatever lay ahead, ${charName} was ready to face it with unwavering determination.`;

        const data = {
            content: content,
            html_content: content.split('\n\n').map(p => `<p>${p}</p>`).join(''),
            word_count: this.storySegments.join(' ').split(/\s+/).length + content.split(/\s+/).length,
            segment_count: this.storySegments.length + 1,
            choices: [
                "Continue with more action and adventure",
                "Develop the characters and relationships",
                "Introduce a surprising twist",
                "Build towards the climax"
            ]
        };

        await this.appendToStory(data);

        if (this.storySegments.length % 3 === 0) {
            this.addChapterMarker();
        }

        this.showLoading(false);
    }

    async appendToStory(data) {
        const storyContent = document.getElementById('storyContent');
        if (storyContent) {
            const divider = document.createElement('div');
            divider.className = 'story-divider';
            divider.textContent = '• • •';
            storyContent.appendChild(divider);

            const segmentDiv = document.createElement('div');
            segmentDiv.className = 'story-segment';
            segmentDiv.dataset.index = this.storySegments.length;
            storyContent.appendChild(segmentDiv);

            if (this.isTypingEnabled && data.content) {
                await this.typeText(segmentDiv, data.html_content || `<p>${this.escapeHtml(data.content)}</p>`);
            } else {
                segmentDiv.innerHTML = data.html_content || `<p>${this.escapeHtml(data.content)}</p>`;
            }
        }

        this.storySegments.push(data.content);
        this.updateStats(data);

        const mood = this.analyzeMood(data.content);
        if (mood !== this.currentMood) {
            this.addToHistory('mood_change', { from: this.currentMood, to: mood });
        }
        this.updateMoodIndicator(mood);
        this.extractCharacters(data.content);

        if (data.choices?.length > 0) {
            this.displayChoices(data.choices);
        }

        storyContent.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }

    showCustomInput() {
        const storyChoices = document.getElementById('storyChoices');
        if (!storyChoices) return;
        storyChoices.innerHTML = `
            <div class="choices-title">What would you like to happen?</div>
            <textarea id="customChoice" class="text-input" rows="3" placeholder="Describe what you want to happen next..."></textarea>
            <div class="nav-buttons" style="margin-top: 16px;">
                <button class="btn btn-ghost" onclick="app.showContinueOptions()">Cancel</button>
                <button class="btn btn-primary" onclick="app.submitCustomChoice()">Continue Story</button>
            </div>
        `;
        document.getElementById('customChoice')?.focus();
    }

    showContinueOptions() {
        const defaultChoices = [
            "Continue with more action and adventure",
            "Develop the characters and relationships",
            "Introduce a surprising twist",
            "Build towards the climax"
        ];
        this.displayChoices(defaultChoices);
    }

    submitCustomChoice() {
        const input = document.getElementById('customChoice');
        const choice = input?.value.trim();
        if (choice) this.selectChoice(choice);
    }

    // ==================== Typing Effect ====================

    async typeText(element, html) {
        element.innerHTML = '';
        const temp = document.createElement('div');
        temp.innerHTML = html;
        const text = temp.textContent || '';

        element.innerHTML = html;
        element.style.opacity = '0';
        await new Promise(r => setTimeout(r, 100));
        element.style.transition = 'opacity 0.5s ease';
        element.style.opacity = '1';
    }

    // ==================== Mood & Characters ====================

    analyzeMood(text) {
        const lower = text.toLowerCase();
        const moodKeywords = {
            happy: ['joy','happy','laugh','smile','celebrate','wonderful','delight'],
            sad: ['sad','tears','grief','loss','mourn','weep','sorrow'],
            tense: ['danger','threat','fight','battle','clash','urgent','desperate'],
            romantic: ['love','heart','kiss','embrace','passion','tender','desire'],
            mysterious: ['mystery','secret','hidden','shadow','unknown','enigma','whisper'],
            adventurous: ['adventure','quest','journey','explore','discover','brave','hero']
        };

        let bestMood = 'neutral';
        let bestScore = 0;
        for (const [mood, keywords] of Object.entries(moodKeywords)) {
            const score = keywords.filter(k => lower.includes(k)).length;
            if (score > bestScore) { bestScore = score; bestMood = mood; }
        }
        return bestMood;
    }

    updateMoodIndicator(mood) {
        this.currentMood = mood;
        const moodData = this.moodThemes[mood] || this.moodThemes.neutral;
        const indicator = document.getElementById('moodIndicator');
        if (indicator) {
            indicator.querySelector('.mood-icon').textContent = moodData.icon;
            indicator.querySelector('.mood-text').textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
        }
        document.documentElement.style.setProperty('--current-mood-color', moodData.color);
    }

    extractCharacters(text) {
        const charName = this.responses['char_1'];
        if (charName && !this.characters.find(c => c.name === charName)) {
            this.characters.push({ name: charName, role: 'Protagonist', mentions: 1 });
        }
        if (charName) {
            const char = this.characters.find(c => c.name === charName);
            if (char) char.mentions++;
        }
        this.updateCharacterPanel();
    }

    updateCharacterPanel() {
        const panel = document.getElementById('characterPanel');
        if (!panel) return;
        if (this.characters.length === 0) {
            panel.innerHTML = '<p class="empty-characters">Characters will appear as your story unfolds...</p>';
            return;
        }
        panel.innerHTML = this.characters.map(c => `
            <div class="character-card">
                <div class="character-avatar">${c.name.charAt(0).toUpperCase()}</div>
                <div class="character-info">
                    <div class="character-name">${this.escapeHtml(c.name)}</div>
                    <div class="character-role">${this.escapeHtml(c.role)}</div>
                </div>
            </div>
        `).join('');
    }

    // ==================== UI Utilities ====================

    showSection(section) {
        const questionSection = document.getElementById('questionSection');
        const storySection = document.getElementById('storySection');
        const loadingSection = document.getElementById('loadingSection');

        questionSection?.classList.remove('hidden');
        storySection?.classList.remove('active');
        loadingSection?.classList.remove('active');

        if (section === 'question') {
            questionSection?.classList.remove('hidden');
        } else if (section === 'story') {
            questionSection?.classList.add('hidden');
            storySection?.classList.add('active');
        }
    }

    showLoading(show, message = 'Loading...') {
        const loadingSection = document.getElementById('loadingSection');
        const loadingText = document.getElementById('loadingText');
        if (show) {
            document.getElementById('questionSection')?.classList.add('hidden');
            document.getElementById('storySection')?.classList.remove('active');
            loadingSection?.classList.add('active');
            if (loadingText) loadingText.textContent = message;
        } else {
            loadingSection?.classList.remove('active');
            if (this.storySegments.length > 0) {
                document.getElementById('storySection')?.classList.add('active');
            }
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        const notificationText = notification?.querySelector('.notification-text');
        const notificationIcon = notification?.querySelector('.notification-icon');
        if (!notification) return;
        const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
        if (notificationIcon) notificationIcon.textContent = icons[type] || 'ℹ️';
        if (notificationText) notificationText.textContent = message;
        notification.className = `notification ${type} show`;
        setTimeout(() => { notification.classList.remove('show'); }, 4000);
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('storyforge-theme', this.theme);
        const btn = document.getElementById('themeToggle');
        if (btn) btn.textContent = this.theme === 'dark' ? '☀️' : '🌙';
        this.showNotification(`${this.theme === 'dark' ? 'Dark' : 'Light'} theme activated`, 'info');
    }

    toggleSound() {
        this.isSoundEnabled = !this.isSoundEnabled;
        localStorage.setItem('storyforge-sound', this.isSoundEnabled);
        const btn = document.getElementById('soundToggle');
        if (btn) btn.textContent = this.isSoundEnabled ? '🔊' : '🔇';
        this.showNotification(`Sound ${this.isSoundEnabled ? 'enabled' : 'disabled'}`, 'info');
    }

    toggleReadingMode() {
        this.isReadingMode = !this.isReadingMode;
        document.body.classList.toggle('reading-mode', this.isReadingMode);
        this.showNotification(`Reading mode ${this.isReadingMode ? 'on' : 'off'}`, 'info');
    }

    toggleShortcutsHint() {
        const hint = document.getElementById('shortcutsHint');
        hint?.classList.toggle('show');
    }

    playSound(type) {
        if (!this.isSoundEnabled) return;
        try {
            if (!this.audioContext) this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            osc.connect(gain);
            gain.connect(this.audioContext.destination);
            gain.gain.value = 0.05;

            const sounds = {
                click: { freq: 800, dur: 0.05 },
                success: { freq: 523, dur: 0.15 },
                error: { freq: 200, dur: 0.2 }
            };
            const s = sounds[type] || sounds.click;
            osc.frequency.value = s.freq;
            osc.type = 'sine';
            gain.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + s.dur);
            osc.start();
            osc.stop(this.audioContext.currentTime + s.dur);
        } catch (e) {}
    }

    // ==================== Save/Load/Export ====================

    saveState() {
        this.undoStack.push({
            segments: [...this.storySegments],
            chapter: this.currentChapter,
            mood: this.currentMood
        });
        this.redoStack = [];
        this.updateUndoRedoButtons();
    }

    undo() {
        if (this.undoStack.length === 0) return;
        this.redoStack.push({
            segments: [...this.storySegments],
            chapter: this.currentChapter,
            mood: this.currentMood
        });
        const state = this.undoStack.pop();
        this.storySegments = state.segments;
        this.currentChapter = state.chapter;
        this.updateMoodIndicator(state.mood);
        this.rebuildStoryDisplay();
        this.updateUndoRedoButtons();
        this.showNotification('Undone', 'info');
    }

    redo() {
        if (this.redoStack.length === 0) return;
        this.undoStack.push({
            segments: [...this.storySegments],
            chapter: this.currentChapter,
            mood: this.currentMood
        });
        const state = this.redoStack.pop();
        this.storySegments = state.segments;
        this.currentChapter = state.chapter;
        this.updateMoodIndicator(state.mood);
        this.rebuildStoryDisplay();
        this.updateUndoRedoButtons();
        this.showNotification('Redone', 'info');
    }

    updateUndoRedoButtons() {
        const undoBtn = document.getElementById('undoBtn');
        const redoBtn = document.getElementById('redoBtn');
        if (undoBtn) undoBtn.disabled = this.undoStack.length === 0;
        if (redoBtn) redoBtn.disabled = this.redoStack.length === 0;
    }

    rebuildStoryDisplay() {
        const storyContent = document.getElementById('storyContent');
        if (!storyContent) return;
        storyContent.innerHTML = '';

        this.storySegments.forEach((segment, i) => {
            if (i > 0) {
                const divider = document.createElement('div');
                divider.className = 'story-divider';
                divider.textContent = '• • •';
                storyContent.appendChild(divider);
            }
            if (i % 3 === 0) {
                const marker = document.createElement('div');
                marker.className = 'chapter-marker';
                marker.innerHTML = `
                    <div class="chapter-number">Chapter ${Math.floor(i / 3) + 1}</div>
                    <div class="chapter-divider"></div>
                `;
                storyContent.appendChild(marker);
            }
            const div = document.createElement('div');
            div.className = 'story-segment';
            div.innerHTML = segment.split('\n\n').map(p => `<p>${p}</p>`).join('');
            storyContent.appendChild(div);
        });

        this.updateStats({
            word_count: this.storySegments.join(' ').split(/\s+/).length,
            segment_count: this.storySegments.length
        });

        this.showContinueOptions();
    }

    saveCurrentStory() {
        if (this.storySegments.length === 0) {
            this.showNotification('No story to save yet', 'warning');
            return;
        }
        const story = {
            id: Date.now(),
            title: `Story by ${this.responses['char_1'] || 'Unknown'}`,
            date: new Date().toLocaleDateString(),
            segments: this.storySegments,
            responses: this.responses,
            characters: this.characters
        };
        this.savedStories.push(story);
        localStorage.setItem('storyforge-stories', JSON.stringify(this.savedStories));
        this.showNotification('Story saved!', 'success');
    }

    showLoadStories() {
        if (this.savedStories.length === 0) {
            this.showNotification('No saved stories found', 'info');
            return;
        }
        const list = this.savedStories.map(s => `
            <div class="saved-story-item" style="padding:12px;margin:8px 0;background:var(--bg-glass);border-radius:8px;cursor:pointer;border:1px solid var(--border-color);" onclick="app.loadSavedStory(${s.id})">
                <strong>${this.escapeHtml(s.title)}</strong>
                <div style="font-size:0.8rem;color:var(--text-muted);">${s.date} · ${s.segments.length} chapter(s)</div>
            </div>
        `).join('');

        const modal = this.createModal('Saved Stories', list);
        document.body.appendChild(modal);
    }

    loadSavedStory(id) {
        const story = this.savedStories.find(s => s.id === id);
        if (!story) return;
        this.storySegments = story.segments;
        this.responses = story.responses || {};
        this.characters = story.characters || [];
        this.closeAllModals();
        this.showSection('story');
        this.rebuildStoryDisplay();
        this.updateCharacterPanel();
        this.showNotification('Story loaded!', 'success');
    }

    addBookmark() {
        if (this.storySegments.length === 0) {
            this.showNotification('No story to bookmark', 'warning');
            return;
        }
        const bookmark = {
            id: Date.now(),
            segment: this.storySegments.length,
            preview: this.storySegments[this.storySegments.length - 1].substring(0, 100) + '...',
            date: new Date().toLocaleString()
        };
        this.bookmarks.push(bookmark);
        localStorage.setItem('storyforge-bookmarks', JSON.stringify(this.bookmarks));
        this.showNotification('Bookmark added!', 'success');
    }

    addToHistory(type, data) {
        this.storyHistory.push({ type, data, time: new Date().toLocaleTimeString() });
    }

    showJourney() {
        if (this.storyHistory.length === 0) {
            this.showNotification('No journey to show yet', 'info');
            return;
        }
        const items = this.storyHistory.map(h => `
            <div style="padding:8px 0;border-bottom:1px solid var(--border-color);font-size:0.85rem;">
                <span style="color:var(--text-muted);">${h.time}</span> — ${h.type}
                ${h.data.choice ? ': ' + this.escapeHtml(h.data.choice.substring(0, 60)) : ''}
            </div>
        `).join('');
        const modal = this.createModal('Story Journey', items);
        document.body.appendChild(modal);
    }

    addChapterMarker() {
        this.currentChapter++;
        const storyContent = document.getElementById('storyContent');
        if (!storyContent) return;
        const marker = document.createElement('div');
        marker.className = 'chapter-marker';
        const titles = ['The Turning Point', 'Rising Action', 'The Revelation', 'The Climax', 'Resolution', 'Epilogue'];
        marker.innerHTML = `
            <div class="chapter-number">Chapter ${this.currentChapter}</div>
            <div class="chapter-title">${titles[(this.currentChapter - 2) % titles.length]}</div>
            <div class="chapter-divider"></div>
        `;
        storyContent.appendChild(marker);
    }

    showExportOptions() {
        if (this.storySegments.length === 0) {
            this.showNotification('No story to export', 'warning');
            return;
        }
        const modal = this.createModal('Export Story', `
            <div class="modal-actions" style="display:flex;flex-direction:column;gap:12px;">
                <button class="btn btn-primary" onclick="app.exportAs('txt')">📄 Export as Text (.txt)</button>
                <button class="btn btn-primary" onclick="app.exportAs('html')">🌐 Export as HTML</button>
                <button class="btn btn-ghost" onclick="app.closeAllModals()">Cancel</button>
            </div>
        `);
        document.body.appendChild(modal);
    }

    exportAs(format) {
        const fullStory = this.storySegments.join('\n\n---\n\n');
        const title = `Story by ${this.responses['char_1'] || 'StoryForge AI'}`;

        if (format === 'txt') {
            const blob = new Blob([`${title}\n${'='.repeat(40)}\n\n${fullStory}`], { type: 'text/plain' });
            this._downloadBlob(blob, `${title}.txt`);
        } else if (format === 'html') {
            const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>${this.escapeHtml(title)}</title><style>body{font-family:Georgia,serif;max-width:700px;margin:40px auto;padding:20px;line-height:1.8;color:#333;background:#fafaf8;}h1{text-align:center;color:#1a1a2e;border-bottom:2px solid #e0e0e0;padding-bottom:10px;}.segment{margin:20px 0;}.divider{text-align:center;color:#999;margin:30px 0;}</style></head><body><h1>${this.escapeHtml(title)}</h1>${this.storySegments.map(s => `<div class="segment">${s.split('\n\n').map(p => `<p>${p}</p>`).join('')}</div><div class="divider">• • •</div>`).join('')}<footer style="text-align:center;color:#999;margin-top:40px;"><p>Generated by StoryForge AI</p></footer></body></html>`;
            const blob = new Blob([html], { type: 'text/html' });
            this._downloadBlob(blob, `${title}.html`);
        }
        this.closeAllModals();
        this.showNotification('Story exported!', 'success');
    }

    _downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // ==================== Modal ====================

    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content" style="background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:16px;padding:24px;max-width:500px;width:90%;max-height:80vh;overflow-y:auto;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                    <h3 style="margin:0;color:var(--text-primary);">${title}</h3>
                    <button onclick="app.closeAllModals()" style="background:none;border:none;color:var(--text-secondary);font-size:1.5rem;cursor:pointer;">×</button>
                </div>
                ${content}
            </div>
        `;
        modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:10000;backdrop-filter:blur(4px);';
        modal.addEventListener('click', (e) => { if (e.target === modal) this.closeAllModals(); });
        return modal;
    }

    closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(m => m.remove());
    }

    // ==================== Settings ====================

    openSettings() {
        document.getElementById('settingsPanel')?.classList.add('active');
        document.getElementById('settingsOverlay')?.classList.add('active');
    }

    closeSettings() {
        document.getElementById('settingsPanel')?.classList.remove('active');
        document.getElementById('settingsOverlay')?.classList.remove('active');
    }

    saveSettings() {
        this.isTypingEnabled = document.getElementById('typingEffect')?.checked ?? true;
        this.isSoundEnabled = document.getElementById('soundEffects')?.checked ?? true;
        localStorage.setItem('storyforge-sound', this.isSoundEnabled);
        this.showNotification('Settings saved!', 'success');
        this.closeSettings();
    }
}

// Initialize the app
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new StoryForgeApp();
});
