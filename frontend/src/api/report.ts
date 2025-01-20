import request from '../utils/request'

export interface ReportQuery {
  page: number
  pageSize: number
  searchQuery?: string
  timeRange?: string
  reportType?: string
}

export interface ScoreData {
  reportId: string
  completeness: number
  accuracy: number
  professionalism: number
  comment: string
}

// 获取报告列表
export const getReportList = (params: ReportQuery) => {
  return request({
    url: '/api/reports',
    method: 'get',
    params
  })
}

// 获取报告详情
export const getReportDetail = (id: string) => {
  return request({
    url: `/api/reports/${id}`,
    method: 'get'
  })
}

// 提交报告评分
export const submitReportScore = (data: ScoreData) => {
  return request({
    url: '/api/reports/score',
    method: 'post',
    data
  })
}

// 下载报告
export const downloadReport = (id: string) => {
  return request({
    url: `/api/reports/${id}/download`,
    method: 'get',
    responseType: 'blob'
  })
}
