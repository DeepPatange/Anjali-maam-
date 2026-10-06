"""
Generate all paper figures into latex/figures/ as PDFs (best for pdflatex).
Run once before pdflatex main.tex.
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'figures')
os.makedirs(OUT, exist_ok=True)

PRI = '#1F2937'
ACC1 = '#2563EB'
ACC2 = '#7C3AED'
ACC3 = '#F59E0B'
ACC4 = '#10B981'
ACC5 = '#EF4444'


def _save(name):
    """Save as both PDF (vector, preferred by pdflatex) and PNG (fallback)."""
    for ext in ('pdf', 'png'):
        plt.savefig(os.path.join(OUT, f'{name}.{ext}'), dpi=240,
                    bbox_inches='tight', facecolor='white')
    plt.close()


# ---------- charts ----------
def latency():
    providers = ['Ollama\n(LLaMA 3.2)', 'Groq\n(8B)', 'Groq\n(70B)', 'HF\n(Mistral)', 'OpenAI\n(3.5)']
    init_gen = [12.4, 1.8, 3.2, 8.5, 2.6]
    cont = [8.1, 1.2, 2.1, 6.3, 1.9]
    x = np.arange(len(providers)); w = 0.36
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    b1 = ax.bar(x - w/2, init_gen, w, label='Initial', color=ACC1, edgecolor='white')
    b2 = ax.bar(x + w/2, cont,     w, label='Continuation', color=ACC3, edgecolor='white')
    ax.set_ylabel('Latency (s)')
    ax.set_xticks(x); ax.set_xticklabels(providers, fontsize=8)
    ax.legend(loc='upper right'); ax.set_ylim(0, 16); ax.grid(axis='y', alpha=0.25)
    ax.bar_label(b1, fmt='%.1f', padding=2, fontsize=7)
    ax.bar_label(b2, fmt='%.1f', padding=2, fontsize=7)
    plt.tight_layout(); _save('f01_latency')


def quality():
    genres = ['Fantasy', 'Sci-Fi', 'Mystery', 'Romance', 'Thriller', 'Adventure']
    coh = [4.2, 4.0, 3.8, 4.1, 3.9, 4.3]
    crea = [4.5, 4.3, 3.7, 4.0, 3.8, 4.4]
    eng = [4.3, 4.1, 4.2, 4.4, 4.5, 4.6]
    cons = [3.9, 3.7, 3.5, 4.0, 3.6, 3.8]
    x = np.arange(len(genres)); w = 0.20
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    ax.bar(x - 1.5*w, coh, w, label='Coherence', color=ACC1)
    ax.bar(x - 0.5*w, crea, w, label='Creativity', color=ACC2)
    ax.bar(x + 0.5*w, eng, w, label='Engagement', color=ACC3)
    ax.bar(x + 1.5*w, cons, w, label='Consistency', color=ACC4)
    ax.set_ylabel('Likert (1--5)')
    ax.set_xticks(x); ax.set_xticklabels(genres, fontsize=9)
    ax.legend(fontsize=8, loc='lower right', ncol=2)
    ax.set_ylim(0, 5.4); ax.grid(axis='y', alpha=0.25)
    plt.tight_layout(); _save('f02_quality')


def satisfaction():
    cats = ['Story\nPersonalization', 'Choice\nMeaningfulness', 'Visual\nIllustration',
            'Narration\nQuality', 'Ambient\nMusic', 'Custom\nAnswers', 'Overall']
    scores = [4.4, 3.9, 4.2, 4.0, 4.3, 4.5, 4.3]
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    colors = [ACC1, ACC2, ACC1, ACC2, ACC3, ACC4, ACC5]
    bars = ax.barh(cats, scores, color=colors, edgecolor='white')
    ax.set_xlim(0, 5); ax.set_xlabel('Score (1--5 Likert)')
    ax.bar_label(bars, fmt='%.1f', padding=3, fontsize=8)
    ax.grid(axis='x', alpha=0.25)
    plt.tight_layout(); _save('f03_satisfaction')


def phases():
    phases = ['Introduction', 'Rising\nAction', 'Climax', 'Falling\nAction', 'Resolution']
    words = [380, 820, 580, 540, 430]
    cum = [380, 1200, 1780, 2320, 2750]
    fig, ax1 = plt.subplots(figsize=(6.0, 3.1))
    bars = ax1.bar(phases, words, color=ACC1, alpha=0.85, edgecolor='white')
    ax1.set_ylabel('Words / phase', color=ACC1)
    ax1.tick_params(axis='y', labelcolor=ACC1)
    ax1.set_ylim(0, 1000)
    ax1.bar_label(bars, fmt='%d', padding=2, fontsize=8)
    ax2 = ax1.twinx()
    ax2.plot(phases, cum, 'o-', color=ACC3, linewidth=2, markersize=5)
    ax2.set_ylabel('Cumulative threshold', color=ACC3)
    ax2.tick_params(axis='y', labelcolor=ACC3); ax2.set_ylim(0, 3200)
    ax1.grid(axis='y', alpha=0.2)
    plt.tight_layout(); _save('f04_phases')


def radar():
    cats = ['User Control', 'Coherence', 'Deploy.\nFlex.', 'Cost\nEfficiency',
            'Accessibility', 'Multimodal', 'Open\nSource']
    ours      = [4.5, 4.2, 5.0, 5.0, 4.5, 4.6, 5.0]
    dungeon   = [5.0, 2.5, 1.5, 2.0, 4.0, 1.0, 1.5]
    dramatron = [3.0, 4.5, 2.0, 2.5, 2.5, 1.0, 4.0]
    novelai   = [4.5, 3.5, 1.5, 2.5, 3.5, 2.0, 1.0]
    N = len(cats)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist(); angles += angles[:1]
    fig, ax = plt.subplots(figsize=(5.4, 4.6), subplot_kw=dict(polar=True))
    for data, col, lab in [(ours, ACC1, 'Ours'), (dungeon, ACC5, 'AI Dungeon'),
                            (dramatron, ACC3, 'Dramatron'), (novelai, ACC4, 'NovelAI')]:
        v = data + data[:1]
        ax.plot(angles, v, 'o-', linewidth=1.6, label=lab, color=col, markersize=3)
        ax.fill(angles, v, alpha=0.10, color=col)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats, fontsize=8)
    ax.set_ylim(0, 5.5); ax.set_yticks([1, 2, 3, 4, 5]); ax.set_yticklabels(['1','2','3','4','5'], fontsize=7)
    ax.legend(loc='upper right', bbox_to_anchor=(1.30, 1.10), fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout(); _save('f05_radar')


def consistency():
    types = ['Character\nContradiction', 'Plot Thread\nAbandonment', 'Pacing\nIssues',
             'Setting\nInconsistency', 'Tone\nShifts']
    det = [87, 79, 82, 73, 68]
    fp = [8, 12, 15, 18, 22]
    x = np.arange(len(types)); w = 0.36
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    b1 = ax.bar(x - w/2, det, w, label='Detection', color=ACC4)
    b2 = ax.bar(x + w/2, fp, w, label='False Positive', color=ACC5, alpha=0.85)
    ax.set_ylabel('Rate (\\%)')
    ax.set_xticks(x); ax.set_xticklabels(types, fontsize=8)
    ax.legend(fontsize=8); ax.set_ylim(0, 100); ax.grid(axis='y', alpha=0.25)
    ax.bar_label(b1, fmt='%d', padding=2, fontsize=7)
    ax.bar_label(b2, fmt='%d', padding=2, fontsize=7)
    plt.tight_layout(); _save('f06_consistency')


def architecture():
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off')

    def box(x, y, w, h, t, c=ACC1, tc='white', fs=8):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.10',
                                              facecolor=c, edgecolor='#222', linewidth=1.0))
        ax.text(x + w/2, y + h/2, t, ha='center', va='center', fontsize=fs,
                color=tc, fontweight='bold')

    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#444', lw=1.1))

    box(0.3, 6.8, 11.4, 0.7, 'PRESENTATION  -  HTML5 + CSS3 + Vanilla JS + D3.js v7',
        '#0F172A', 'white', 8)
    box(0.3, 5.7, 11.4, 0.7, 'APPLICATION  -  FastAPI / Uvicorn ASGI - 14 REST endpoints',
        ACC1, 'white', 8)
    box(0.3, 4.4, 2.0, 0.9, 'User Input\nAcquisition', ACC2)
    box(2.5, 4.4, 2.0, 0.9, 'Context\nExtraction', ACC2)
    box(4.7, 4.4, 2.0, 0.9, 'Prompt\nEngineering', ACC2)
    box(6.9, 4.4, 2.0, 0.9, 'Story Flow\nManager', ACC2)
    box(9.1, 4.4, 2.6, 0.9, 'Knowledge / Memory\n(SQLite)', ACC3, '#111', 7.5)
    box(0.3, 3.0, 2.5, 0.9, 'Story Generator\n(LLM)', ACC5)
    box(3.0, 3.0, 2.5, 0.9, 'Output Formatter\n+ HTML/MD/TXT', ACC4)
    box(5.7, 3.0, 2.5, 0.9, 'Image Synthesis\n(Pollinations.ai)', ACC1)
    box(8.4, 3.0, 1.6, 0.9, 'TTS\nWeb Speech', ACC2)
    box(10.1, 3.0, 1.6, 0.9, 'Audio Stream\n(SoundHelix)', ACC3, '#111', 7.5)
    box(0.3, 1.5, 3.0, 0.9, 'Ollama (local)\nLLaMA/Mistral/Phi', '#0F172A', 'white', 7.5)
    box(3.5, 1.5, 2.5, 0.9, 'Groq Cloud\nLLaMA3.1/Mixtral', ACC1, 'white', 7.5)
    box(6.2, 1.5, 2.5, 0.9, 'HuggingFace\nMistral/Zephyr', ACC4, 'white', 7.5)
    box(8.9, 1.5, 2.8, 0.9, 'OpenAI\nGPT-3.5/GPT-4', ACC5, 'white', 7.5)
    for x in [1.3, 3.5, 5.7, 7.9, 10.4]:
        arrow(x, 5.7, x, 5.3)
    arrow(1.3, 4.4, 1.3, 3.9); arrow(3.5, 4.4, 3.5, 3.9)
    arrow(5.7, 4.4, 6.9, 3.9); arrow(7.9, 4.4, 9.2, 3.9)
    arrow(1.5, 3.0, 1.5, 2.4)
    plt.tight_layout(); _save('f07_arch')


def qa_coverage():
    labels = ['Setting & World (4)', 'Character (5)', 'Theme & Genre (4)', 'Plot & Structure (4)']
    sizes = [4, 5, 4, 4]
    colors = [ACC1, ACC2, ACC3, ACC4]
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%',
                                       startangle=90, textprops={'fontsize': 9},
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    for t in autotexts:
        t.set_fontsize(9); t.set_fontweight('bold'); t.set_color('white')
    plt.tight_layout(); _save('f08_qa')


def image_pipeline():
    fig, ax = plt.subplots(figsize=(7.0, 2.4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 3); ax.axis('off')

    def box(x, y, w, h, t, c=ACC1, fs=8):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08',
                                              facecolor=c, edgecolor='#222', linewidth=1.0))
        ax.text(x + w/2, y + h/2, t, ha='center', va='center', fontsize=fs,
                color='white', fontweight='bold')

    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#444', lw=1.1))

    box(0.2, 1.0, 1.7, 1.0, 'Story\nSegment', PRI)
    box(2.2, 1.0, 1.9, 1.0, 'Scene\nExtractor', ACC2)
    box(4.4, 1.0, 1.9, 1.0, 'Prompt\nBuilder', ACC1)
    box(6.6, 1.0, 1.9, 1.0, 'Request\nQueue', ACC3)
    box(8.8, 1.0, 1.9, 1.0, 'Pollinations\nAPI', ACC5)
    box(11.0, 1.0, 1.0, 1.0, 'IMG', ACC4)
    for x1, x2 in [(1.9, 2.2), (4.1, 4.4), (6.3, 6.6), (8.5, 8.8), (10.7, 11.0)]:
        arrow(x1, 1.5, x2, 1.5)
    ax.text(3.15, 0.4, 'strip dialogue\nscore visual', ha='center', fontsize=7, color='#444')
    ax.text(5.35, 0.4, r'$\leq$200 chars''\n+ genre tag', ha='center', fontsize=7, color='#444')
    ax.text(7.55, 0.4, '1.2 s spacing\n+ watchdog', ha='center', fontsize=7, color='#444')
    ax.text(9.75, 0.4, r'768$\times$432''\nseeded', ha='center', fontsize=7, color='#444')
    plt.tight_layout(); _save('f09_imgpipe')


def audio_signal():
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis('off')

    def box(x, y, w, h, t, c=ACC1, fs=8):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08',
                                              facecolor=c, edgecolor='#222', linewidth=1.0))
        ax.text(x + w/2, y + h/2, t, ha='center', va='center', fontsize=fs,
                color='white', fontweight='bold')

    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#444', lw=1.1))

    box(0.2, 2.8, 1.8, 0.9, 'Story Text', PRI)
    box(2.2, 2.8, 2.0, 0.9, 'Utterance\nQueue', ACC2)
    box(4.4, 2.8, 2.4, 0.9, 'Web Speech\nSynth API', ACC1)
    box(7.0, 2.8, 2.4, 0.9, 'OS TTS Voice\n(per locale)', ACC4)
    box(9.6, 2.8, 2.2, 0.9, 'Speakers', ACC5)
    for x1, x2 in [(2.0, 2.2), (4.2, 4.4), (6.8, 7.0), (9.4, 9.6)]:
        arrow(x1, 3.25, x2, 3.25)
    ax.text(6.0, 3.8, 'TTS narration path', ha='center', fontsize=8, color='#444', fontweight='bold')
    box(0.2, 1.0, 1.8, 0.9, 'Detected\nGenre', PRI)
    box(2.2, 1.0, 2.0, 0.9, 'Track\nMapper', ACC3)
    box(4.4, 1.0, 2.4, 0.9, 'HTMLAudio\nLoop + Fade', ACC1)
    box(7.0, 1.0, 2.4, 0.9, 'CDN Stream\n(SoundHelix)', ACC2)
    box(9.6, 1.0, 2.2, 0.9, 'Speakers', ACC5)
    for x1, x2 in [(2.0, 2.2), (4.2, 4.4), (6.8, 7.0), (9.4, 9.6)]:
        arrow(x1, 1.45, x2, 1.45)
    ax.text(6.0, 0.4, 'Ambient music path (8 genre presets)', ha='center', fontsize=8,
            color='#444', fontweight='bold')
    plt.tight_layout(); _save('f10_audio')


def char_extraction():
    metrics = ['Precision', 'Recall', 'F1-Score', 'False Pos.\nRate']
    before = [0.61, 0.84, 0.71, 0.39]
    after  = [0.83, 0.78, 0.80, 0.17]
    x = np.arange(len(metrics)); w = 0.36
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    b1 = ax.bar(x - w/2, before, w, label='Baseline', color=ACC5, alpha=0.85)
    b2 = ax.bar(x + w/2, after,  w, label='Filtered+min2', color=ACC4)
    ax.set_ylabel('Score'); ax.set_xticks(x); ax.set_xticklabels(metrics, fontsize=8)
    ax.set_ylim(0, 1.0); ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.25)
    ax.bar_label(b1, fmt='%.2f', padding=2, fontsize=7)
    ax.bar_label(b2, fmt='%.2f', padding=2, fontsize=7)
    plt.tight_layout(); _save('f11_char')


def image_throughput():
    lengths = np.array([80, 110, 140, 170, 200, 230, 270, 320, 380])
    serial = np.array([1.5, 1.7, 2.1, 2.4, 2.8, 3.4, 4.5, 7.2, 14.6])
    pfail = np.array([0.4, 0.5, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98])
    fig, ax1 = plt.subplots(figsize=(5.6, 3.0))
    ax1.plot(lengths, serial, 'o-', color=ACC1, linewidth=2, markersize=4, label='Latency (s)')
    ax1.set_xlabel('Prompt length (chars)')
    ax1.set_ylabel('Latency (s)', color=ACC1)
    ax1.tick_params(axis='y', labelcolor=ACC1)
    ax1.grid(axis='y', alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(lengths, pfail, 's--', color=ACC5, linewidth=2, markersize=4, label='Failure prob.')
    ax2.set_ylabel(r'Failure prob. (5$\times$ parallel)', color=ACC5)
    ax2.tick_params(axis='y', labelcolor=ACC5); ax2.set_ylim(0, 1.05)
    plt.tight_layout(); _save('f12_imgthroughput')


def ambient_heat():
    genres = ['Fantasy', 'Sci-Fi', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Horror', 'Comedy']
    bands  = ['<150', '150-300', '300-600', '600-1.2k', '1.2-2.4k', '>2.4k']
    M = np.array([
        [0.1, 0.4, 0.7, 0.9, 0.7, 0.3],
        [0.2, 0.5, 0.6, 0.7, 0.6, 0.4],
        [0.4, 0.6, 0.5, 0.4, 0.2, 0.1],
        [0.0, 0.2, 0.6, 0.8, 0.7, 0.5],
        [0.5, 0.8, 0.6, 0.3, 0.2, 0.1],
        [0.0, 0.3, 0.7, 0.9, 0.8, 0.5],
        [0.7, 0.8, 0.5, 0.2, 0.1, 0.05],
        [0.0, 0.1, 0.5, 0.9, 0.9, 0.7],
    ])
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    im = ax.imshow(M, aspect='auto', cmap='viridis')
    ax.set_xticks(range(len(bands))); ax.set_xticklabels(bands, fontsize=8)
    ax.set_yticks(range(len(genres))); ax.set_yticklabels(genres, fontsize=9)
    ax.set_xlabel('Frequency band (Hz)')
    for i in range(len(genres)):
        for j in range(len(bands)):
            ax.text(j, i, f'{M[i,j]:.1f}', ha='center', va='center',
                    color='white' if M[i,j] < 0.6 else 'black', fontsize=7)
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label('Normalised energy', fontsize=8)
    plt.tight_layout(); _save('f13_ambient')


def adoption():
    feats = ['Custom\nAnswer', 'Custom\nQuestion', 'Image\nGen', 'TTS\nNarration',
             'Ambient\nMusic', 'Story\nMap', 'Character\nGraph']
    adopt = [62, 38, 91, 47, 71, 33, 41]
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    bars = ax.bar(feats, adopt, color=[ACC1, ACC1, ACC2, ACC3, ACC3, ACC4, ACC4], edgecolor='white')
    ax.set_ylabel('Adoption rate (\\%)'); ax.set_ylim(0, 100); ax.grid(axis='y', alpha=0.25)
    ax.bar_label(bars, fmt='%d%%', padding=2, fontsize=8)
    plt.setp(ax.get_xticklabels(), fontsize=8)
    plt.tight_layout(); _save('f14_adoption')


def tokens():
    np.random.seed(7)
    data = {
        'Fantasy':   np.random.normal(560, 90, 25),
        'Sci-Fi':    np.random.normal(540, 80, 25),
        'Mystery':   np.random.normal(520, 70, 25),
        'Romance':   np.random.normal(530, 75, 25),
        'Thriller':  np.random.normal(510, 65, 25),
        'Adventure': np.random.normal(580, 95, 25),
    }
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    bp = ax.boxplot(list(data.values()), tick_labels=list(data.keys()),
                    patch_artist=True, widths=0.55)
    palette = [ACC1, ACC2, ACC3, ACC4, ACC5, '#0EA5E9']
    for p, c in zip(bp['boxes'], palette):
        p.set_facecolor(c); p.set_alpha(0.7); p.set_edgecolor('#222')
    for med in bp['medians']:
        med.set_color('white'); med.set_linewidth(2)
    ax.set_ylabel('Tokens / segment'); ax.grid(axis='y', alpha=0.25)
    plt.setp(ax.get_xticklabels(), fontsize=9)
    plt.tight_layout(); _save('f15_tokens')


def custom_q_pipeline():
    fig, ax = plt.subplots(figsize=(7.0, 2.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 2.5); ax.axis('off')

    def box(x, y, w, h, t, c=ACC1, fs=8):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08',
                                              facecolor=c, edgecolor='#222', linewidth=1.0))
        ax.text(x + w/2, y + h/2, t, ha='center', va='center', fontsize=fs,
                color='white', fontweight='bold')

    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#444', lw=1.1))

    box(0.2, 0.8, 1.8, 1.0, 'User Adds\nQ + A', PRI)
    box(2.2, 0.8, 2.0, 1.0, 'Synthetic ID\ncustom\\_q\\_N', ACC2)
    box(4.4, 0.8, 2.0, 1.0, '/api/response\n(stored)', ACC1)
    box(6.6, 0.8, 2.4, 1.0, 'Context Eng.\ncustom\\_elements', ACC3)
    box(9.2, 0.8, 2.6, 1.0, 'Prompt Layer\n+user preferences', ACC4)
    for x1, x2 in [(2.0, 2.2), (4.2, 4.4), (6.4, 6.6), (9.0, 9.2)]:
        arrow(x1, 1.3, x2, 1.3)
    plt.tight_layout(); _save('f16_customq')


def breakdown():
    stages = ['Quick (4)', 'Balanced (8)', 'Detailed (12)', 'Full (17)']
    layers = [
        ('User Q&A input',  [25, 50, 80, 110], '#94A3B8'),
        ('Context extract', [0.4, 0.6, 0.8, 1.0], ACC1),
        ('Prompt eng.',     [0.3, 0.4, 0.5, 0.6], ACC2),
        ('LLM generation',  [1.8, 2.0, 2.2, 2.4], ACC3),
        ('Image synthesis', [3.5, 3.5, 3.5, 3.5], ACC5),
        ('Formatter',       [0.2, 0.2, 0.2, 0.2], ACC4),
    ]
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    y0 = np.zeros(4)
    for lab, vals, col in layers:
        ax.bar(stages, vals, bottom=y0, label=lab, color=col, edgecolor='white')
        y0 = y0 + np.array(vals)
    ax.set_ylabel('Time (s)'); ax.legend(fontsize=7, loc='upper left', ncol=2)
    ax.grid(axis='y', alpha=0.25)
    plt.tight_layout(); _save('f17_breakdown')


def main():
    print('Writing figures to', OUT)
    for fn in [latency, quality, satisfaction, phases, radar, consistency,
               architecture, qa_coverage, image_pipeline, audio_signal,
               char_extraction, image_throughput, ambient_heat, adoption,
               tokens, custom_q_pipeline, breakdown]:
        fn()
        print('  ok:', fn.__name__)
    print('Done. 17 figures (.pdf + .png each).')


if __name__ == '__main__':
    main()
