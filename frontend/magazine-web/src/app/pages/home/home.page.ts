import { NgFor, NgIf } from '@angular/common';
import { Component, OnDestroy, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ArticlesApi } from '../../features/articles/articles.api';
import { Article } from '../../features/articles/articles.types';
import { isExternalLink, normalizeHeroSlides } from '../../features/site/hero-slides.util';
import { slideLinkToRouterCommands } from '../../features/site/slide-link.util';
import { SITE_DEFAULTS, SiteSettingsApi } from '../../features/site/site-settings.api';
import { HeroSlide, SiteSettings } from '../../features/site/site-settings.types';

type GridCard = {
  title: string;
  excerpt: string;
  link: string;
  img?: string;
  isNews?: boolean;
  isKahani?: boolean;
};

type HeroSlideView = HeroSlide & { imageUrl: string };

const FALLBACK_CARDS: GridCard[] = [
  { title: 'कहानी', excerpt: 'दिल को छू लेने वाली कहानियाँ...', link: '/category/kahani' },
  { title: 'कविता', excerpt: 'कविता, ग़ज़ल, दोहे...', link: '/category/kavita' },
  { title: 'लेख', excerpt: 'विचार और अनुभव...', link: '/editorial' },
  { title: 'मनोरंजन', excerpt: 'मनोरंजन की दुनिया...', link: '/interviews' },
  { title: 'यात्रा', excerpt: 'घूमने की जगहें...', link: '/kitchen' }
];

@Component({
  standalone: true,
  selector: 'app-home-page',
  imports: [NgFor, NgIf, RouterLink, FormsModule],
  templateUrl: './home.page.html',
  styleUrl: './home.page.scss'
})
export class HomePage implements OnDestroy {
  private readonly articlesApi = inject(ArticlesApi);
  private readonly siteApi = inject(SiteSettingsApi);

  protected readonly homeRowLimit = 5;
  protected readonly homeNewsLimit = 8;
  protected readonly isExternalLink = isExternalLink;
  protected readonly slideRouterLink = slideLinkToRouterCommands;
  protected newsletterEmail = '';
  protected newsletterSending = false;
  protected newsletterSent = false;
  protected newsletterMessage = '';

  protected readonly activeSlide = signal(0);
  protected readonly site = signal<SiteSettings>({ ...SITE_DEFAULTS, hero_slides: [...SITE_DEFAULTS.hero_slides] });
  protected readonly gridCards = signal<GridCard[]>(FALLBACK_CARDS.slice(0, 5));
  protected readonly newsCards = signal<GridCard[]>([]);
  protected readonly showSeeAll = signal(false);
  protected readonly showSeeAllNews = signal(false);
  protected readonly seeAllLink = signal('/category/kahani');
  protected readonly heroSlides = signal<HeroSlideView[]>(this.buildHeroSlides(SITE_DEFAULTS.hero_slides));

  private timer: ReturnType<typeof setInterval> | null = null;
  private paused = false;

  constructor() {
    this.startAuto();
    this.siteApi.getPublic().subscribe((s) => {
      this.site.set(s);
      this.heroSlides.set(this.buildHeroSlides(s.hero_slides));
      this.startAuto();
    });

    this.articlesApi.listPublished(100).subscribe((articles) => {
      if (!articles.length) return;
      const sorted = [...articles].sort((a, b) => {
        const da = a.published_at ? Date.parse(a.published_at) : 0;
        const db = b.published_at ? Date.parse(b.published_at) : 0;
        return db - da;
      });
      const newsList = sorted.filter((a) => this.isNewsArticle(a));
      const storyList = sorted.filter((a) => !this.isNewsArticle(a) && (!a.part_number || a.part_number <= 1));

      const newsTop = newsList.slice(0, this.homeNewsLimit);
      this.newsCards.set(newsTop.map((a) => this.articleCard(a)));
      this.showSeeAllNews.set(newsList.length > this.homeNewsLimit);

      const top = storyList.slice(0, this.homeRowLimit);
      this.showSeeAll.set(storyList.length > this.homeRowLimit);
      this.seeAllLink.set('/category/love-story');
      if (top.length) {
        this.gridCards.set(top.map((a) => this.articleCard(a)));
      }
    });
  }

  ngOnDestroy() {
    this.stopAuto();
  }

  slideCount(): number {
    return this.heroSlides().length;
  }

  pauseAuto() {
    this.paused = true;
    this.stopAuto();
  }

  resumeAuto() {
    this.paused = false;
    this.startAuto();
  }

  goTo(i: number) {
    this.activeSlide.set(i);
    if (!this.paused) this.startAuto();
  }

  next() {
    const n = this.slideCount();
    if (!n) return;
    this.activeSlide.update((i) => (i + 1) % n);
    if (!this.paused) this.startAuto();
  }

  prev() {
    const n = this.slideCount();
    if (!n) return;
    this.activeSlide.update((i) => (i - 1 + n) % n);
    if (!this.paused) this.startAuto();
  }

  private buildHeroSlides(slides: HeroSlide[]): HeroSlideView[] {
    return normalizeHeroSlides(slides).map((slide) => ({
      ...slide,
      imageUrl: this.siteApi.resolveAsset(slide.image)
    }));
  }

  onNewsletterSubmit(event: Event) {
    event.preventDefault();
    const email = this.newsletterEmail.trim();
    if (!email) {
      this.newsletterMessage = 'कृपया ईमेल दर्ज करें।';
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      this.newsletterMessage = 'सही ईमेल पता दर्ज करें।';
      return;
    }
    this.newsletterSending = true;
    this.newsletterMessage = '';
    setTimeout(() => {
      this.newsletterSending = false;
      this.newsletterSent = true;
      this.newsletterMessage = 'धन्यवाद! न्यूज़लेटर सुविधा जल्द शुरू होगी — आपका ईमेल सुरक्षित रहेगा।';
      this.newsletterEmail = '';
    }, 600);
  }

  private isNewsArticle(a: Article): boolean {
    return a.category_slug === 'lekh' || (a.tags?.includes('समाचार') ?? false);
  }

  private isMoralKahani(a: Article): boolean {
    return a.tags?.includes('नैतिक कहानी') ?? false;
  }

  cardImage(c: GridCard): string {
    if (c.img) return c.img;
    return this.siteApi.resolveAsset('/uploads/images/news-card.svg');
  }

  onCardImgError(ev: Event, c: GridCard): void {
    const img = ev.target as HTMLImageElement;
    if (img.dataset['fallback'] === '1') return;
    img.dataset['fallback'] = '1';
    const key = c.link.replace(/^\/article\//, '').replace(/-bhag-\d+$/, '');
    if (c.isKahani && key) {
      img.src = this.siteApi.resolveAsset(`/uploads/images/kahani/${key}.svg`);
    } else if (!c.isNews && key) {
      img.src = this.siteApi.resolveAsset(`/uploads/images/love-story/${key}.svg`);
    } else {
      img.src = this.siteApi.resolveAsset('/uploads/images/news-card.svg');
    }
  }

  private articleCard(a: Article): GridCard {
    const title = a.title.replace(/\s*—\s*भाग\s*\d+\s*$/i, '').trim() || a.title;
    const seriesKey = (a.series_slug ?? a.slug).replace(/-bhag-\d+$/, '');
    let img = a.cover_url ? this.siteApi.resolveAsset(a.cover_url) : undefined;
    if (!img && a.category_slug === 'love-story') {
      img = this.siteApi.resolveAsset(`/uploads/images/love-story/${seriesKey}.jpg`);
    }
    if (!img && (this.isMoralKahani(a) || a.category_slug === 'kahani')) {
      img = this.siteApi.resolveAsset(`/uploads/images/kahani/${a.slug}.svg`);
    }
    if (!img && this.isNewsArticle(a)) {
      img = this.siteApi.resolveAsset('/uploads/images/news-card.svg');
    }
    return {
      title,
      excerpt: a.excerpt || '',
      link: `/article/${a.slug}`,
      img,
      isNews: this.isNewsArticle(a),
      isKahani: this.isMoralKahani(a) || a.category_slug === 'kahani'
    };
  }

  private startAuto() {
    this.stopAuto();
    const n = this.slideCount();
    if (n < 2) return;
    this.timer = setInterval(() => this.activeSlide.update((i) => (i + 1) % n), 5000);
  }

  private stopAuto() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}
