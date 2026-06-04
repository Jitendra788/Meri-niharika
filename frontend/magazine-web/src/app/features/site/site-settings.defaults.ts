import { SiteSettings } from './site-settings.types';

export const SITE_DEFAULTS: SiteSettings = {
  hero_tagline_line1: 'हर नारी की कहानी, हर भावना की ज़ुबानी',
  hero_tagline_line2: 'Love Stories, Live Forever',
  hero_slides: [
    {
      image: '/hero-banner.png',
      category_label: 'सोसायटी',
      title: 'धर्म नहीं ऐजुकेशन जरूरी',
      link: '/article/power-of-education'
    }
  ],
  intro_editorial_title: 'संपादक की बात',
  intro_editorial_text:
    'Ishqora में आपका स्वागत है। यह मंच हर नारी की आवाज़, हर रचनाकार की भावना और हर पाठक के लिए समर्पित है।',
  intro_editorial_image: '/hero-banner.png',
  intro_letter_title: 'खत लिख दो...',
  intro_letter_text: 'अपनी बात, सुझाव या रचना हमें लिखकर भेजें। आपका खत हमारे लिए महत्वपूर्ण है।',
  intro_letter_image: '/hero-banner.png',
  bottom_archive_title: 'बोलते पत्थर',
  bottom_archive_text: 'इतिहास की झाँकी — पुरानी यादें और किस्से...',
  bottom_newsletter_title: 'हमसे जुड़ें',
  bottom_newsletter_text: 'नई कहानियाँ और अपडेट ईमेल पर पाएँ।',
  bottom_social_title: 'हमें फॉलो करें',
  bottom_social_text: 'सोशल मीडिया पर जुड़ें।',
  editorial_page_title: 'संपादकीय',
  editorial_page_body: 'यहाँ संपादक का संदेश दिखेगा।'
};
