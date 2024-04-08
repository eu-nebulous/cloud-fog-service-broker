{{/*
Expand the name of the chart.
*/}}
{{- define "nebulous-cloud-fog-service-broker.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "nebulous-cloud-fog-service-broker.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nebulous-cloud-fog-service-broker.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nebulous-cloud-fog-service-broker.labels" -}}
helm.sh/chart: {{ include "nebulous-cloud-fog-service-broker.chart" . }}
{{ include "nebulous-cloud-fog-service-broker.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "nebulous-cloud-fog-service-broker.frontend.labels" -}}
helm.sh/chart: {{ include "nebulous-cloud-fog-service-broker.chart" . }}
{{ include "nebulous-cloud-fog-service-broker.frontend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "nebulous-cloud-fog-service-broker.postgresql.labels" -}}
helm.sh/chart: {{ include "nebulous-cloud-fog-service-broker.chart" . }}
{{ include "nebulous-cloud-fog-service-broker.postgresql.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nebulous-cloud-fog-service-broker.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nebulous-cloud-fog-service-broker.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "nebulous-cloud-fog-service-broker.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nebulous-cloud-fog-service-broker.name" . }}-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "nebulous-cloud-fog-service-broker.postgresql.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nebulous-cloud-fog-service-broker.name" . }}-postgresql
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "nebulous-cloud-fog-service-broker.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "nebulous-cloud-fog-service-broker.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
