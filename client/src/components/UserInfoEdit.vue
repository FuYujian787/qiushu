<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  user: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['save'])

const editing = ref(false)
const editForm = ref({
  nickname: props.user?.nickname || '',
  college: props.user?.college || '',
  major: props.user?.major || '',
  grade: props.user?.grade || '',
  phone: props.user?.phone || '',
  email: props.user?.email || '',
})

function startEdit() {
  editForm.value = {
    nickname: props.user?.nickname || '',
    college: props.user?.college || '',
    major: props.user?.major || '',
    grade: props.user?.grade || '',
    phone: props.user?.phone || '',
    email: props.user?.email || '',
  }
  editing.value = true
}

async function saveProfile() {
  try {
    await api.put('/user/profile', {
      nickname: editForm.value.nickname,
      college: editForm.value.college,
      major: editForm.value.major,
      grade: editForm.value.grade,
      phone: editForm.value.phone,
      email: editForm.value.email,
    })
    ElMessage.success('资料已更新')
    editing.value = false
    emit('save', editForm.value)
  } catch (err) {
    ElMessage.error(err.message || '更新失败')
  }
}
</script>

<template>
  <div class="user-info-edit">
    <div v-if="!editing" class="info-display">
      <div class="info-row">
        <span class="info-label">昵称</span>
        <span class="info-value">{{ user.nickname || '书友' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">学院</span>
        <span class="info-value">{{ user.college || '未设置' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">专业</span>
        <span class="info-value">{{ user.major || '未设置' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">年级</span>
        <span class="info-value">{{ user.grade || '未设置' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">手机号</span>
        <span class="info-value">{{ user.phone || '未绑定' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">邮箱</span>
        <span class="info-value">{{ user.email || '未绑定' }}</span>
      </div>
      <button class="edit-btn" @click="startEdit">编辑资料</button>
    </div>

    <div v-else class="edit-form">
      <div class="field">
        <label>昵称</label>
        <input v-model="editForm.nickname" class="input" placeholder="输入昵称" />
      </div>
      <div class="field">
        <label>学院</label>
        <input v-model="editForm.college" class="input" placeholder="输入学院" />
      </div>
      <div class="field">
        <label>专业</label>
        <input v-model="editForm.major" class="input" placeholder="输入专业" />
      </div>
      <div class="field">
        <label>年级</label>
        <input v-model="editForm.grade" class="input" placeholder="输入年级" />
      </div>
      <div class="field">
        <label>手机号</label>
        <input v-model="editForm.phone" class="input" placeholder="输入手机号" />
      </div>
      <div class="field">
        <label>邮箱</label>
        <input v-model="editForm.email" class="input" placeholder="输入邮箱" />
      </div>
      <div class="edit-actions">
        <button class="save-btn" @click="saveProfile">保存</button>
        <button class="cancel-btn" @click="editing = false">取消</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-info-edit {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
}

.info-display { display: flex; flex-direction: column; gap: 12px; }

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
}

.info-label {
  width: 64px;
  font-size: 13px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.info-value { font-size: 14px; color: var(--text-primary); }

.edit-btn {
  margin-top: 12px;
  padding: 8px 20px;
  border: 1px solid var(--accent-primary);
  border-radius: 6px;
  background: transparent;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  width: fit-content;
  transition: all 0.2s;
}

.edit-btn:hover { background: var(--accent-primary); color: #fff; }

[data-theme="cyber"] .edit-btn:hover { background: linear-gradient(135deg, #00D4FF, #A855F7); }

.edit-form { display: flex; flex-direction: column; gap: 12px; }

.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: 13px; color: var(--text-secondary); }

.input {
  padding: 8px 12px;
  border: 1px solid var(--border-default);
  border-radius: 6px;
  background: var(--surface-primary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
}

.input:focus { border-color: var(--accent-primary); }

.edit-actions { display: flex; gap: 8px; margin-top: 4px; }

.save-btn {
  padding: 8px 24px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
}

[data-theme="cyber"] .save-btn { background: linear-gradient(135deg, #00D4FF, #A855F7); }

.cancel-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-default);
  border-radius: 6px;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
}

.cancel-btn:hover { border-color: var(--accent-primary); color: var(--accent-primary); }
</style>
