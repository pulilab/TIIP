export default function ({ app, store, route, redirect }) {
  const user = store.state.user.profile
  const routeName = route.name.split('___')[0]
  const routeObserver = [
    'organisation-management',
    'organisation-management-edit-id',
    'organisation-management-new',
    'organisation-management-id',
  ]
  const permissions =
    (user && user.is_superuser) ||
    (user && user.global_portfolio_owner) ||
    (user && user.manager.length > 0)
  if (routeObserver.includes(routeName)) {
    if (permissions) {
      if (
        routeName === 'organisation-management-new' &&
        !user.global_portfolio_owner
      ) {
        redirect(
          app.localePath({
            name: 'organisation',
            params: { organisation: '-' },
          })
        )
      }
    } else {
      redirect(
        app.localePath({
          name: 'organisation',
          params: { organisation: '-' },
        })
      )
    }
  }
}
