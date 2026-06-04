import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AdminSession } from './admin.session';

export const adminGuard: CanActivateFn = () => {
  const session = inject(AdminSession);
  const router = inject(Router);
  if (session.isLoggedIn()) return true;
  return router.createUrlTree(['/admin/login']);
};
