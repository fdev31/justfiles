<template>
    <dialog>
        <article>
            <header>
                <span style="font-size: 200%" v-html="title" />
            </header>

            <form>
                <slot />
                <button type="submit" aria-label="apply" formmethod="dialog" @click="on_validate"><span
                        class="pi pi-check" /></button>
                <button type="submit" aria-label="close" formmethod="dialog" formnovalidate class="secondary">
                    <span class="pi pi-times" />
                </button>
            </form>
        </article>
    </dialog>
</template>

<script setup>
defineProps({
    title: String(),
    on_validate: Function,
});
</script>

<style scoped>
article {
    padding-bottom: 0;
}
</style>
