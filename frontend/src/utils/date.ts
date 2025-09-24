/**
 * 日期时间工具函数
 */

// 日期格式化选项
interface DateFormatOptions {
  format?: string
  locale?: string
}

// 时间格式化选项
interface TimeFormatOptions {
  format?: '12h' | '24h'
  showSeconds?: boolean
}

/**
 * 格式化日期
 */
export function formatDate(
  date: string | number | Date | null | undefined,
  options: DateFormatOptions = {}
): string {
  if (!date) return ''

  const { format = 'YYYY-MM-DD', locale = 'zh-CN' } = options

  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return ''

    // 使用 Intl.DateTimeFormatter 进行本地化格式化
    if (format === 'locale') {
      return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }).format(dateObj)
    }

    // 自定义格式化
    const year = dateObj.getFullYear()
    const month = String(dateObj.getMonth() + 1).padStart(2, '0')
    const day = String(dateObj.getDate()).padStart(2, '0')

    return format
      .replace('YYYY', String(year))
      .replace('MM', month)
      .replace('DD', day)
      .replace('M', String(dateObj.getMonth() + 1))
      .replace('D', String(dateObj.getDate()))
  } catch {
    return ''
  }
}

/**
 * 格式化时间
 */
export function formatTime(
  date: string | number | Date | null | undefined,
  options: TimeFormatOptions = {}
): string {
  if (!date) return ''

  const { format = '24h', showSeconds = false } = options

  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return ''

    const hours = dateObj.getHours()
    const minutes = String(dateObj.getMinutes()).padStart(2, '0')
    const seconds = String(dateObj.getSeconds()).padStart(2, '0')

    if (format === '12h') {
      const period = hours >= 12 ? 'PM' : 'AM'
      const displayHours = hours % 12 || 12
      return `${displayHours}:${minutes}${showSeconds ? `:${seconds}` : ''} ${period}`
    } else {
      return `${String(hours).padStart(2, '0')}:${minutes}${showSeconds ? `:${seconds}` : ''}`
    }
  } catch {
    return ''
  }
}

/**
 * 格式化日期时间
 */
export function formatDateTime(
  date: string | number | Date | null | undefined,
  options: DateFormatOptions & TimeFormatOptions = {}
): string {
  if (!date) return ''

  const dateStr = formatDate(date, options)
  const timeStr = formatTime(date, options)

  return `${dateStr} ${timeStr}`
}

/**
 * 获取相对时间
 */
export function getRelativeTime(
  date: string | number | Date | null | undefined,
  locale: string = 'zh-CN'
): string {
  if (!date) return ''

  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return ''

    const now = new Date()
    const diff = now.getTime() - dateObj.getTime()

    // 使用 Intl.RelativeTimeFormat
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })

    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    const weeks = Math.floor(days / 7)
    const months = Math.floor(days / 30)
    const years = Math.floor(days / 365)

    if (years > 0) return rtf.format(-years, 'year')
    if (months > 0) return rtf.format(-months, 'month')
    if (weeks > 0) return rtf.format(-weeks, 'week')
    if (days > 0) return rtf.format(-days, 'day')
    if (hours > 0) return rtf.format(-hours, 'hour')
    if (minutes > 0) return rtf.format(-minutes, 'minute')
    return rtf.format(-seconds, 'second')
  } catch {
    return ''
  }
}

/**
 * 计算两个日期之间的天数差
 */
export function getDaysBetween(
  startDate: string | Date,
  endDate: string | Date
): number {
  try {
    const start = new Date(startDate)
    const end = new Date(endDate)

    if (isNaN(start.getTime()) || isNaN(end.getTime())) return 0

    const diffTime = Math.abs(end.getTime() - start.getTime())
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  } catch {
    return 0
  }
}

/**
 * 判断是否为今天
 */
export function isToday(date: string | Date): boolean {
  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return false

    const today = new Date()
    return (
      dateObj.getDate() === today.getDate() &&
      dateObj.getMonth() === today.getMonth() &&
      dateObj.getFullYear() === today.getFullYear()
    )
  } catch {
    return false
  }
}

/**
 * 判断是否为昨天
 */
export function isYesterday(date: string | Date): boolean {
  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return false

    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)

    return (
      dateObj.getDate() === yesterday.getDate() &&
      dateObj.getMonth() === yesterday.getMonth() &&
      dateObj.getFullYear() === yesterday.getFullYear()
    )
  } catch {
    return false
  }
}

/**
 * 获取星期几
 */
export function getWeekday(
  date: string | Date,
  locale: string = 'zh-CN'
): string {
  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return ''

    return new Intl.DateTimeFormat(locale, { weekday: 'long' }).format(dateObj)
  } catch {
    return ''
  }
}

/**
 * 获取星期几（短格式）
 */
export function getWeekdayShort(
  date: string | Date,
  locale: string = 'zh-CN'
): string {
  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return ''

    return new Intl.DateTimeFormat(locale, { weekday: 'short' }).format(dateObj)
  } catch {
    return ''
  }
}

/**
 * 添加天数
 */
export function addDays(
  date: string | Date,
  days: number
): Date {
  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return new Date()

    const result = new Date(dateObj)
    result.setDate(result.getDate() + days)
    return result
  } catch {
    return new Date()
  }
}

/**
 * 添加小时
 */
export function addHours(
  date: string | Date,
  hours: number
): Date {
  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) return new Date()

    const result = new Date(dateObj)
    result.setHours(result.getHours() + hours)
    return result
  } catch {
    return new Date()
  }
}

/**
 * 获取月份的第一天
 */
export function getFirstDayOfMonth(
  year: number,
  month: number
): Date {
  return new Date(year, month - 1, 1)
}

/**
 * 获取月份的最后一天
 */
export function getLastDayOfMonth(
  year: number,
  month: number
): Date {
  return new Date(year, month, 0)
}

/**
 * 获取月份的天数
 */
export function getDaysInMonth(
  year: number,
  month: number
): number {
  return new Date(year, month, 0).getDate()
}

/**
 * 格式化时间范围
 */
export function formatTimeRange(
  startTime: string | Date,
  endTime: string | Date,
  options: { format?: '12h' | '24h'; showSeconds?: boolean } = {}
): string {
  const start = formatTime(startTime, options)
  const end = formatTime(endTime, options)
  return `${start} - ${end}`
}

/**
 * 获取时间戳
 */
export function getTimestamp(date?: string | Date): number {
  return date ? new Date(date).getTime() : Date.now()
}

/**
 * 验证日期格式
 */
export function isValidDate(date: string | Date): boolean {
  try {
    const dateObj = new Date(date)
    return !isNaN(dateObj.getTime())
  } catch {
    return false
  }
}

/**
 * 解析日期字符串
 */
export function parseDate(dateString: string): Date | null {
  try {
    const date = new Date(dateString)
    return isNaN(date.getTime()) ? null : date
  } catch {
    return null
  }
}

/**
 * 格式化持续时间（毫秒）
 */
export function formatDuration(milliseconds: number): string {
  if (milliseconds < 1000) {
    return `${milliseconds}ms`
  }

  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) {
    return `${days}天 ${hours % 24}小时`
  }

  if (hours > 0) {
    return `${hours}小时 ${minutes % 60}分钟`
  }

  if (minutes > 0) {
    return `${minutes}分钟 ${seconds % 60}秒`
  }

  return `${seconds}秒`
}

/**
 * 格式化持续时间（秒）
 */
export function formatDurationSeconds(seconds: number): string {
  return formatDuration(seconds * 1000)
}