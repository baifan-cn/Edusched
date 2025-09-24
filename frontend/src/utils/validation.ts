import type { FormValidationError } from '@/types'

// 邮箱验证正则
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// 手机号验证正则（中国大陆）
const PHONE_REGEX = /^1[3-9]\d{9}$/

// 密码强度验证正则
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/

// 表单验证工具类
export class FormValidator {
  /**
   * 验证必填字段
   */
  static required(value: any, fieldName: string): FormValidationError | null {
    if (value === undefined || value === null || value === '') {
      return {
        field: fieldName,
        message: `${fieldName}不能为空`
      }
    }
    return null
  }

  /**
   * 验证邮箱格式
   */
  static email(value: string, fieldName: string): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    if (!EMAIL_REGEX.test(value)) {
      return {
        field: fieldName,
        message: `${fieldName}格式不正确`
      }
    }
    return null
  }

  /**
   * 验证手机号格式
   */
  static phone(value: string, fieldName: string): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    if (!PHONE_REGEX.test(value)) {
      return {
        field: fieldName,
        message: `${fieldName}格式不正确`
      }
    }
    return null
  }

  /**
   * 验证密码强度
   */
  static password(value: string, fieldName: string): FormValidationError | null {
    if (!value) {
      return {
        field: fieldName,
        message: `${fieldName}不能为空`
      }
    }

    if (!PASSWORD_REGEX.test(value)) {
      return {
        field: fieldName,
        message: `${fieldName}必须包含大小写字母、数字和特殊字符，且至少8位`
      }
    }
    return null
  }

  /**
   * 验证最小长度
   */
  static minLength(value: string, fieldName: string, min: number): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    if (value.length < min) {
      return {
        field: fieldName,
        message: `${fieldName}长度不能少于${min}个字符`
      }
    }
    return null
  }

  /**
   * 验证最大长度
   */
  static maxLength(value: string, fieldName: string, max: number): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    if (value.length > max) {
      return {
        field: fieldName,
        message: `${fieldName}长度不能超过${max}个字符`
      }
    }
    return null
  }

  /**
   * 验证数字范围
   */
  static range(value: number, fieldName: string, min: number, max: number): FormValidationError | null {
    if (value < min || value > max) {
      return {
        field: fieldName,
        message: `${fieldName}必须在${min}到${max}之间`
      }
    }
    return null
  }

  /**
   * 验证正则表达式
   */
  static pattern(value: string, fieldName: string, regex: RegExp, message?: string): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    if (!regex.test(value)) {
      return {
        field: fieldName,
        message: message || `${fieldName}格式不正确`
      }
    }
    return null
  }

  /**
   * 验证日期格式
   */
  static date(value: string, fieldName: string): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    const date = new Date(value)
    if (isNaN(date.getTime())) {
      return {
        field: fieldName,
        message: `${fieldName}格式不正确`
      }
    }
    return null
  }

  /**
   * 验证日期范围
   */
  static dateRange(startDate: string, endDate: string, fieldName: string): FormValidationError | null {
    if (!startDate || !endDate) return null // 如果非必填，跳过验证

    const start = new Date(startDate)
    const end = new Date(endDate)

    if (start > end) {
      return {
        field: fieldName,
        message: `${fieldName}的结束日期不能早于开始日期`
      }
    }
    return null
  }

  /**
   * 验证时间格式
   */
  static time(value: string, fieldName: string): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/
    if (!timeRegex.test(value)) {
      return {
        field: fieldName,
        message: `${fieldName}格式不正确，请使用HH:mm格式`
      }
    }
    return null
  }

  /**
   * 验证时间范围
   */
  static timeRange(startTime: string, endTime: string, fieldName: string): FormValidationError | null {
    if (!startTime || !endTime) return null // 如果非必填，跳过验证

    if (startTime >= endTime) {
      return {
        field: fieldName,
        message: `${fieldName}的结束时间不能早于开始时间`
      }
    }
    return null
  }

  /**
   * 验证URL格式
   */
  static url(value: string, fieldName: string): FormValidationError | null {
    if (!value) return null // 如果非必填，跳过验证

    try {
      new URL(value)
      return null
    } catch {
      return {
        field: fieldName,
        message: `${fieldName}格式不正确`
      }
    }
  }

  /**
   * 验证数字
   */
  static numeric(value: any, fieldName: string): FormValidationError | null {
    if (!value && value !== 0) return null // 如果非必填，跳过验证

    if (isNaN(Number(value))) {
      return {
        field: fieldName,
        message: `${fieldName}必须是数字`
      }
    }
    return null
  }

  /**
   * 验证整数
   */
  static integer(value: any, fieldName: string): FormValidationError | null {
    if (!value && value !== 0) return null // 如果非必填，跳过验证

    if (!Number.isInteger(Number(value))) {
      return {
        field: fieldName,
        message: `${fieldName}必须是整数`
      }
    }
    return null
  }

  /**
   * 验证正数
   */
  static positive(value: number, fieldName: string): FormValidationError | null {
    if (!value && value !== 0) return null // 如果非必填，跳过验证

    if (value <= 0) {
      return {
        field: fieldName,
        message: `${fieldName}必须是正数`
      }
    }
    return null
  }

  /**
   * 验证非负数
   */
  static nonNegative(value: number, fieldName: string): FormValidationError | null {
    if (!value && value !== 0) return null // 如果非必填，跳过验证

    if (value < 0) {
      return {
        field: fieldName,
        message: `${fieldName}不能是负数`
      }
    }
    return null
  }

  /**
   * 验证唯一性（异步）
   */
  static async unique(
    value: any,
    fieldName: string,
    checkFn: (value: any) => Promise<boolean>
  ): Promise<FormValidationError | null> {
    if (!value) return null // 如果非必填，跳过验证

    const isUnique = await checkFn(value)
    if (!isUnique) {
      return {
        field: fieldName,
        message: `${fieldName}已存在`
      }
    }
    return null
  }

  /**
   * 批量验证
   */
  static validate(
    data: Record<string, any>,
    rules: Record<string, ((value: any, fieldName: string) => FormValidationError | null)[]>
  ): FormValidationError[] {
    const errors: FormValidationError[] = []

    for (const [field, validators] of Object.entries(rules)) {
      const value = data[field]
      const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

      for (const validator of validators) {
        const error = validator(value, fieldName)
        if (error) {
          errors.push(error)
          break // 某个字段有一个错误就跳过后续验证
        }
      }
    }

    return errors
  }
}

// 导出常用的验证规则
export const validationRules = {
  required: (fieldName: string) => (value: any) => FormValidator.required(value, fieldName),
  email: (fieldName: string) => (value: string) => FormValidator.email(value, fieldName),
  phone: (fieldName: string) => (value: string) => FormValidator.phone(value, fieldName),
  password: (fieldName: string) => (value: string) => FormValidator.password(value, fieldName),
  minLength: (fieldName: string, min: number) => (value: string) => FormValidator.minLength(value, fieldName, min),
  maxLength: (fieldName: string, max: number) => (value: string) => FormValidator.maxLength(value, fieldName, max),
  range: (fieldName: string, min: number, max: number) => (value: number) => FormValidator.range(value, fieldName, min, max),
  date: (fieldName: string) => (value: string) => FormValidator.date(value, fieldName),
  time: (fieldName: string) => (value: string) => FormValidator.time(value, fieldName),
  numeric: (fieldName: string) => (value: any) => FormValidator.numeric(value, fieldName),
  integer: (fieldName: string) => (value: any) => FormValidator.integer(value, fieldName),
  positive: (fieldName: string) => (value: number) => FormValidator.positive(value, fieldName),
  nonNegative: (fieldName: string) => (value: number) => FormValidator.nonNegative(value, fieldName)
}

export default FormValidator