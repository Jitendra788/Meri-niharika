export type HeroSlide = {
  image: string;
  category_label: string;
  title: string;
  link: string;
};

export type SiteSettings = {
  hero_tagline_line1: string;
  hero_tagline_line2: string;
  hero_slides: HeroSlide[];
  intro_editorial_title: string;
  intro_editorial_text: string;
  intro_editorial_image: string;
  intro_letter_title: string;
  intro_letter_text: string;
  intro_letter_image: string;
  bottom_archive_title: string;
  bottom_archive_text: string;
  bottom_newsletter_title: string;
  bottom_newsletter_text: string;
  bottom_social_title: string;
  bottom_social_text: string;
  editorial_page_title: string;
  editorial_page_body: string;
};
