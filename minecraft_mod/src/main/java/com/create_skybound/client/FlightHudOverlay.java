package com.create_skybound.client;

import com.create_skybound.blockentity.SkywayBeaconBlockEntity;
import com.create_skybound.registry.ModItems;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.LayeredDraw;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

public class FlightHudOverlay implements LayeredDraw.Layer {
    @Override
    public void render(GuiGraphics guiGraphics, DeltaTracker deltaTracker) {
        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null || mc.options.hideGui) return;

        boolean wearingVisor = player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.AERONAUT_VISOR.get());
        boolean holdingSextant = player.getMainHandItem().is(ModItems.FLIGHT_SEXTANT.get()) ||
                                player.getOffhandItem().is(ModItems.FLIGHT_SEXTANT.get());

        if (!wearingVisor && !holdingSextant) return;

        Font font = mc.font;
        int screenWidth = mc.getWindow().getGuiScaledWidth();
        int screenHeight = mc.getWindow().getGuiScaledHeight();

        // Left Panel: Altitude & Variometer
        int yLevel = (int) player.getY();
        int seaLevel = player.level().getSeaLevel();
        int deltaSea = yLevel - seaLevel;
        double vy = player.getDeltaMovement().y * 20.0;

        int hudColor = 0xFFD480; // Aeronautics brass gold
        int alertColor = 0xFF5555; // Stall/sink warning

        // Draw compass heading at top center
        float yaw = player.getYRot();
        float heading = (yaw % 360 + 360) % 360;
        String cardinal = getCardinal(heading);
        String headingText = String.format("HDG: %03d° %s", (int) heading, cardinal);
        int headingWidth = font.width(headingText);
        guiGraphics.drawString(font, headingText, (screenWidth - headingWidth) / 2, 12, hudColor, true);

        // Draw altimeter on middle-left
        int altY = screenHeight / 2 - 20;
        String altText = String.format("ALT: %dm (MSL %+dm)", yLevel, deltaSea);
        guiGraphics.drawString(font, altText, 16, altY, hudColor, true);

        // Draw vertical climb rate
        String rateText = String.format("V/S: %+.1f m/s", vy);
        int vsColor = Math.abs(vy) > 8.0 ? alertColor : hudColor;
        guiGraphics.drawString(font, rateText, 16, altY + 12, vsColor, true);

        // Draw horizontal speed
        Vec3 vel = player.getDeltaMovement();
        double speed = Math.sqrt(vel.x * vel.x + vel.z * vel.z) * 20.0;
        String spdText = String.format("SPD: %.1f m/s", speed);
        guiGraphics.drawString(font, spdText, 16, altY + 24, hudColor, true);

        // If beacon nearby, draw beacon bearing on top-right
        SkywayBeaconBlockEntity beacon = SkywayBeaconBlockEntity.findNearest(player.level(), player.position());
        if (beacon != null) {
            BlockPos bPos = beacon.getBlockPos();
            double dx = bPos.getX() + 0.5 - player.getX();
            double dz = bPos.getZ() + 0.5 - player.getZ();
            double dist = Math.sqrt(dx * dx + dz * dz);
            double beaconAngle = (Math.toDegrees(Math.atan2(-dx, dz)) + 360) % 360;

            String beaconText = String.format("BEACON: %dm [%03d° %s]", (int) dist, (int) beaconAngle, getCardinal(beaconAngle));
            int bWidth = font.width(beaconText);
            guiGraphics.drawString(font, beaconText, screenWidth - bWidth - 16, 12, 0x55FF55, true);
        }
    }

    private static String getCardinal(double deg) {
        String[] directions = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        int index = (int) Math.round(((deg % 360) / 45)) % 8;
        return directions[index];
    }
}
