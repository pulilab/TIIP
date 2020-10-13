export const objectToQueryString = (queryParameters) => {
  return queryParameters
    ? Object.entries(queryParameters).reduce(
        (queryString, [key, val], index) => {
          const symbol = queryString.length === 0 ? '?' : '&'
          queryString += typeof val === 'string' ? `${symbol}${key}=${val}` : ''
          return queryString
        },
        ''
      )
    : ''
}
