import { Routes } from '@angular/router';

import { adminGuard } from './admin/admin.guard';
import { categoryArticleMatcher } from './category-article.matcher';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/home/home.page').then((m) => m.HomePage)
  },
  {
    path: 'admin/login',
    loadComponent: () => import('./admin/admin-login.page').then((m) => m.AdminLoginPage)
  },
  {
    path: 'admin',
    loadComponent: () => import('./admin/admin-layout.component').then((m) => m.AdminLayout),
    canActivate: [adminGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./admin/pages/dashboard.page').then((m) => m.AdminDashboardPage)
      },
      {
        path: 'site',
        loadComponent: () => import('./admin/pages/site.page').then((m) => m.AdminSitePage)
      },
      {
        path: 'articles',
        loadComponent: () => import('./admin/pages/articles.page').then((m) => m.AdminArticlesPage)
      },
      {
        path: 'users',
        loadComponent: () => import('./admin/pages/users.page').then((m) => m.AdminUsersPage)
      },
      {
        path: 'archive',
        loadComponent: () => import('./admin/pages/archive.page').then((m) => m.AdminArchivePage)
      }
    ]
  },
  {
    path: 'editorial',
    redirectTo: 'category/lekh',
    pathMatch: 'full'
  },
  {
    path: 'category/:slug',
    loadComponent: () => import('./pages/category/category.page').then((m) => m.CategoryPage)
  },
  {
    path: 'special/:slug',
    loadComponent: () => import('./pages/special/special.page').then((m) => m.SpecialPage)
  },
  {
    path: 'article/:slug',
    loadComponent: () => import('./pages/article/article.page').then((m) => m.ArticlePage)
  },
  {
    path: 'creators',
    loadComponent: () => import('./pages/creators/creators.page').then((m) => m.CreatorsPage)
  },
  {
    path: 'interviews',
    redirectTo: 'category/manoranjan',
    pathMatch: 'full'
  },
  {
    path: 'kitchen',
    redirectTo: 'category/yatra',
    pathMatch: 'full'
  },
  {
    path: 'beauty',
    redirectTo: 'category/swasthya',
    pathMatch: 'full'
  },
  {
    path: 'stars',
    redirectTo: 'category/dharm',
    pathMatch: 'full'
  },
  {
    path: 'archive',
    loadComponent: () => import('./pages/archive/archive.page').then((m) => m.ArchivePage)
  },
  {
    path: 'story/:slug',
    loadComponent: () => import('./pages/story/story.page').then((m) => m.StoryPage)
  },
  {
    path: 'submit',
    loadComponent: () => import('./pages/submit/submit.page').then((m) => m.SubmitPage)
  },
  {
    path: 'open-mic',
    loadComponent: () => import('./pages/open-mic/open-mic.page').then((m) => m.OpenMicPage)
  },
  {
    path: 'certificate',
    loadComponent: () => import('./pages/certificate/certificate.page').then((m) => m.CertificatePage)
  },
  {
    path: 'contact',
    loadComponent: () => import('./pages/contact/contact.page').then((m) => m.ContactPage)
  },
  {
    matcher: categoryArticleMatcher,
    loadComponent: () => import('./pages/article/article.page').then((m) => m.ArticlePage)
  },
  { path: '**', redirectTo: '' }
];
