import { NgIf } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter, map } from 'rxjs';

import { AdminSession } from './admin/admin.session';
import { ApiStatusService } from './core/api-status.service';
import { SITE_EMAIL } from './core/site.config';

@Component({
  selector: 'app-root',
  imports: [NgIf, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('magazine-web');
  protected readonly siteEmail = SITE_EMAIL;
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  protected readonly admin = inject(AdminSession);
  protected readonly apiStatus = inject(ApiStatusService);

  protected readonly lang$ = this.route.queryParamMap.pipe(map((q) => (q.get('lang') === 'en' ? 'en' : 'hi')));
  protected readonly isMobileMenuOpen = signal(false);
  protected readonly url = signal<string>(this.router.url);
  protected readonly isAdminRoute = signal<boolean>(this.router.url.startsWith('/admin'));

  constructor() {
    void this.apiStatus.check();
    this.router.events
      .pipe(
        filter((e): e is NavigationEnd => e instanceof NavigationEnd),
        map((e) => e.urlAfterRedirects)
      )
      .subscribe((u) => {
        this.url.set(u);
        this.isAdminRoute.set(u.startsWith('/admin'));
      });
  }

  protected toggleMobileMenu() {
    this.isMobileMenuOpen.update((v) => !v);
  }

  protected closeMobileMenu() {
    this.isMobileMenuOpen.set(false);
  }

  protected logout() {
    this.admin.logout();
    this.closeMobileMenu();
  }
}
