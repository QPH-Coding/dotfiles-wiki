local keymaps = require("core.keymaps")

require("blink.cmp").setup({
  keymap = { preset = "default" },
  appearance = {
    nerd_font_variant = "mono",
  },
  completion = {
    documentation = { auto_show = false },
  },
  sources = {
    default = { "lsp", "path", "buffer" },
  },
  fuzzy = {
    implementation = "lua",
  },
})

local blink_actions = {
  show = "Show completion menu",
  show_documentation = "Show documentation",
  hide_documentation = "Hide documentation",
  cancel = "Cancel completion",
  accept = "Accept completion",
  select_and_accept = "Accept selected item",
  select_prev = "Select previous item",
  select_next = "Select next item",
  scroll_documentation_up = "Scroll documentation up",
  scroll_documentation_down = "Scroll documentation down",
  show_signature = "Show signature help",
  hide_signature = "Hide signature help",
  snippet_forward = "Jump to next snippet field",
  snippet_backward = "Jump to previous snippet field",
}

local ignored_actions = {
  fallback = true,
  fallback_to_mappings = true,
}

local function blink_summary(actions)
  local summary = {}

  for _, action in ipairs(actions) do
    if type(action) == "function" then
      table.insert(summary, "Custom blink.cmp action")
    elseif not ignored_actions[action] then
      table.insert(summary, blink_actions[action] or action)
    end
  end

  if #summary == 0 then
    return "Fallback to built-in behavior"
  end

  return table.concat(summary, " / ")
end

local blink_preset = require("blink.cmp.keymap.presets").get("default")
local blink_entries = {}

for lhs, actions in pairs(blink_preset) do
  table.insert(blink_entries, {
    mode = "i",
    lhs = lhs,
    desc = blink_summary(actions),
    detail = "blink.cmp default preset",
  })
end

keymaps.register("Blink", blink_entries)

return {
  capabilities = require("blink.cmp").get_lsp_capabilities(),
}
